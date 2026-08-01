"""Pydantic request/response models for the RepoCoder Studio inference API."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    device: str
    baseline_loaded: bool
    finetuned_loaded: bool
    finetuned_error: Optional[str] = None


class TaskInfo(BaseModel):
    task_id: str
    source: str
    target: str
    description: str


class GenerateRequest(BaseModel):
    task_id: str = Field(..., examples=["T1"])
    input_text: str = Field(default="")
    model_type: Literal["baseline", "finetuned"] = "baseline"


class GenerateResponse(BaseModel):
    task_id: str
    model_type: str
    output: str


class CompareRequest(BaseModel):
    task_id: str = Field(..., examples=["T1"])
    input_text: str = Field(default="")


class CompareResponse(BaseModel):
    task_id: str
    baseline_output: str
    finetuned_output: Optional[str] = None
    finetuned_available: bool
