import uuid
import os
from fastapi.responses import FileResponse
from research_and_analyst.utils.model_loader import ModelLoader
from research_and_analyst.workflows.report_generator_workflow import AutonomousReportGenerator
from research_and_analyst.logger import GLOBAL_LOGGER
from research_and_analyst.exception.custom_exception import ResearchAnalystException
from langgraph.checkpoint.memory import MemorySaver

_shared_memory = MemorySaver()

class ReportService:
    def __init__(self):
        self.llm = ModelLoader().load_llm()
        self.reporter = AutonomousReportGenerator(self.llm)
        self.reporter.memory = _shared_memory 
        self.graph = self.reporter.build_graph()
        self.logger = GLOBAL_LOGGER.bind(module="ReportService")

    def start_report_generation(self, topic: str, max_analysts: int):
        """Trigger the autonomous report pipeline."""
        try:
            thread_id = str(uuid.uuid4())
            thread = {"configurable": {"thread_id": thread_id}}
            self.logger.info("Starting report pipeline", topic=topic, thread_id=thread_id)

            for _ in self.graph.stream({"topic": topic, "max_analysts": max_analysts}, thread, stream_mode="values"):
                pass

            return {"thread_id": thread_id, "message": "Pipeline initiated successfully."}
        except Exception as e:
            self.logger.error("Error initiating report generation", error=str(e))
            raise ResearchAnalystException("Failed to start report generation", e)
        
    def submit_feedback(self, thread_id: str, feedback: str):
        """Update human feedback in graph state."""
        try:
            thread = {"configurable": {"thread_id": thread_id}}
            self.graph.update_state(thread, {"human_analyst_feedback": feedback}, as_node="human_feedback")
            self.logger.info("Feedback updated", thread_id=thread_id)
            for _ in self.graph.stream(None, thread, stream_mode="values"):
                pass
            return {"message": "Feedback processed successfully"}
        except Exception as e:
            self.logger.error("Error updating feedback", error=str(e))
            raise ResearchAnalystException("Failed to update feedback", e)