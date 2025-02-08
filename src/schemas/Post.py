from datetime import datetime
from typing import List

from pydantic import BaseModel


class Post(BaseModel):
    description:str 
    media:List[str]
    time_to_publish:datetime