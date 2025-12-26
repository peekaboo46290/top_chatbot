from typing import List, Optional
from pydantic import BaseModel, Field

class Example(BaseModel):
    name: str = Field(..., description="Title or identifier of the example")
    content: str = Field(..., description="The actual example with solution")
    subject: str = Field(..., description="Mathematical subject")
    domain: str = Field(..., description="Specific domain")
    illustrates_theorems: List[str] = Field(default_factory=list, description="Theorems this example illustrates")
    difficulty: str = Field(default="Medium", description="Easy, Medium, or Hard")#for indexing

