from dataclasses import dataclass
from datetime import datetime
from typing import List

from pydantic import BaseModel

@dataclass
class SheduledPost:
    task_id:str
    description:str 
    media:List[str]
    channel:str
