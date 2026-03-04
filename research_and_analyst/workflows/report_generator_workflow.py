import os
import sys
import re
from datetime import datetime
from typing import Optional
from langgraph.types import Send
from jinja2 import Template

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(project_root)

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.tools.tavily_search import TavilySearchResults

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from research_and_analyst.schemas.models import (
    Perspectives,
    GenerateAnalystsState,
    ResearchGraphState,
)
from research_and_analyst.utils.model_loader import ModelLoader
from research_and_analyst.workflows.interview_workflow import InterviewGraphBuilder
from research_and_analyst.prompt_lib.prompt_locator import (
    CREATE_ANALYSTS_PROMPT,
    INTRO_CONCLUSION_INSTRUCTIONS,
    REPORT_WRITER_INSTRUCTIONS,
)
from research_and_analyst.logger import GLOBAL_LOGGER
from research_and_analyst.exception.custom_exception import ResearchAnalystException

class AutonomousReportGenerator:
    """
    Handles the end-to-end autonomous report generation workflow using LangGraph.
    """

    def __init__(self, llm):
        self.llm = llm
        self.memory = MemorySaver()
        self.tavily_search = TavilySearchResults(
            tavily_api_key="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"
        )
        self.logger = GLOBAL_LOGGER.bind(module="AutonomousReportGenerator")

    # ----------------------------------------------------------------------
    
    def create_analyst(self, state: GenerateAnalystsState):
        """Generate analyst personas based on topic and feedback."""
        topic = state["topic"]
        max_analysts = state["max_analysts"]
        human_analyst_feedback = state.get("human_analyst_feedback", "")

        try:
            self.logger.info("Creating analyst personas", topic=topic)
            structured_llm = self.llm.with_structured_output(Perspectives)
            system_prompt = CREATE_ANALYSTS_PROMPT.render(
                topic=topic, max_analysts=max_analysts,
                human_analyst_feedback=human_analyst_feedback,
            )
            analysts = structured_llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content="Generate the set of analysts."),
            ])
            self.logger.info("Analysts created", count=len(analysts.analysts))
            return {"analysts": analysts.analysts}
        except Exception as e:
            self.logger.error("Error creating analysts", error=str(e))
            raise ResearchAnalystException("Failed to create analysts", e)

    # ----------------------------------------------------------------------
    
    def human_feedback(self):
        """Pause node for human analyst feedback."""
        try:
            self.logger.info("Awaiting human feedback")
        except Exception as e:
            self.logger.error("Error during feedback stage", error=str(e))
            raise ResearchAnalystException("Human feedback node failed", e)

    # ----------------------------------------------------------------------
    def write_report(self, state: ResearchGraphState):
        """Compile all report sections into unified content."""
        sections = state.get("sections", [])
        topic = state.get("topic", "")

        try:
            if not sections:
                sections = ["No sections generated — please verify interview stage."]
            self.logger.info("Writing report", topic=topic)
            system_prompt = REPORT_WRITER_INSTRUCTIONS.render(topic=topic)
            report = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content="\n\n".join(sections))
            ])
            self.logger.info("Report written successfully")
            return {"content": report.content}
        except Exception as e:
            self.logger.error("Error writing main report", error=str(e))
            raise ResearchAnalystException("Failed to write main report", e)

    # ----------------------------------------------------------------------
    def write_introduction(self, state: ResearchGraphState):
        """Generate the report introduction."""
        try:
            sections = state["sections"]
            topic = state["topic"]
            formatted_str_sections = "\n\n".join([f"{s}" for s in sections])
            self.logger.info("Generating introduction", topic=topic)
            system_prompt = INTRO_CONCLUSION_INSTRUCTIONS.render(
                topic=topic, formatted_str_sections=formatted_str_sections
            )
            intro = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content="Write the report introduction")
            ])
            self.logger.info("Introduction generated", length=len(intro.content))
            return {"introduction": intro.content}
        except Exception as e:
            self.logger.error("Error generating introduction", error=str(e))
            raise ResearchAnalystException("Failed to generate introduction", e)
        
    # ----------------------------------------------------------------------
    def write_conclusion(self, state: ResearchGraphState):
        """Generate the conclusion section."""
        try:
            sections = state["sections"]
            topic = state["topic"]
            formatted_str_sections = "\n\n".join([f"{s}" for s in sections])
            self.logger.info("Generating conclusion", topic=topic)
            system_prompt = INTRO_CONCLUSION_INSTRUCTIONS.render(
                topic=topic, formatted_str_sections=formatted_str_sections
            )
            conclusion = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content="Write the report conclusion")
            ])
            self.logger.info("Conclusion generated", length=len(conclusion.content))
            return {"conclusion": conclusion.content}
        except Exception as e:
            self.logger.error("Error generating conclusion", error=str(e))
            raise ResearchAnalystException("Failed to generate conclusion", e)
        
    # ----------------------------------------------------------------------
    def finalize_report(self, state: ResearchGraphState):
        """Assemble introduction, content, and conclusion into final report."""
        try:
            content = state["content"]
            self.logger.info("Finalizing report compilation")
            if content.startswith("## Insights"):
                content = content.strip("## Insights")

            sources = None
            if "## Sources" in content:
                try:
                    content, sources = content.split("\n## Sources\n")
                except Exception:
                    pass

            final_report = (
                state["introduction"] + "\n\n---\n\n" +
                content + "\n\n---\n\n" +
                state["conclusion"]
            )
            if sources:
                final_report += "\n\n## Sources\n" + sources

            self.logger.info("Report finalized")
            return {"final_report": final_report}
        except Exception as e:
            self.logger.error("Error finalizing report", error=str(e))
            raise ResearchAnalystException("Failed to finalize report", e)

    # ----------------------------------------------------------------------
        
    