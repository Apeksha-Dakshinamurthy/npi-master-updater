from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class InputData(BaseModel):
    first_name: Optional[str] = Field(default="")
    middle_name: Optional[str] = Field(default="")
    last_name: Optional[str] = Field(default="")
    classification: Optional[str] = Field(default="")
    npi_number: Optional[str] = Field(default="")
    primary_affiliation_name: Optional[str] = Field(default="")

class FinalOutput(BaseModel):
    # Define fields based on expected final_output structure
    # Using a generic dict for flexibility; can be refined later
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SwarmInput(BaseModel):
    input_data: InputData

class SwarmOutput(BaseModel):
    final_output: Optional[FinalOutput]
