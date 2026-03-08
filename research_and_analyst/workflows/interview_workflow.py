from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages import get_buffer_string
from langgraph.types import Send

from research_and_analyst.schemas.models import InterviewState, SearchQuery
from research_and_analyst.prompt_lib.prompt_locator import (
    ANALYST_ASK_QUESTIONS,
    GENERATE_SEARCH_QUERY,
    GENERATE_ANSWERS,
    WRITE_SECTION,
)
from research_and_analyst.logger import GLOBAL_LOGGER
from research_and_analyst.exception.custom_exception import ResearchAnalystException

class InterviewGraphBuilder:
    """
    A class responsible for constructing and managing the Interview Graph workflow.
    Handles the process of:
        1. Analyst generating questions.
        2. Performing relevant web search.
        3. Expert generating answers.
        4. Saving the interview transcript.
        5. Writing a summarized report section.
    """

    def __init__(self, llm, tavily_search):
        """
        Initialize the InterviewGraphBuilder with the LLM model and Tavily search tool.
        """
        self.llm = llm
        self.tavily_search = tavily_search
        self.memory = MemorySaver()
        self.logger = GLOBAL_LOGGER.bind(module="InterviewGraphBuilder")
        
    # ----------------------------------------------------------------------
    # 🔹 Step 1: Analyst generates question
    # ----------------------------------------------------------------------
    def _generate_question(self, state: InterviewState):
        """
        Generate the first question for the interview based on the analyst's persona.
        """
        analyst = state["analyst"]
        messages = state["messages"]

        try:
            self.logger.info("Generating analyst question", analyst=analyst.name)
            system_prompt = ANALYST_ASK_QUESTIONS.render(goals=analyst.persona)
            question = self.llm.invoke([SystemMessage(content=system_prompt)] + messages)
            self.logger.info("Question generated successfully", question_preview=question.content[:200])
            return {"messages": [question]}

        except Exception as e:
            self.logger.error("Error generating analyst question", error=str(e))
            raise ResearchAnalystException("Failed to generate analyst question", e)