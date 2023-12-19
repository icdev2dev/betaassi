from .metathread import MetaThread
from typing import Optional
from pydantic import Field

class BaseThread(MetaThread):
    thread_type: Optional[str] = Field(default="")   
