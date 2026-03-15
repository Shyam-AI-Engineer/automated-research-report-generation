# models.py
import operator
from typing import Annotated, List
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing_extensions import TypedDict