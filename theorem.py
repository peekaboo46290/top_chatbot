from typing import List
from pydantic import BaseModel


class Theorem(BaseModel):
    name:str
    statement: str
    proof: str = "Not provided"
    subject:str #alg or anl ...
    domain: str #top or cal..
    dependencies: List[str]
    t_type:str #lemme or prop ...     
