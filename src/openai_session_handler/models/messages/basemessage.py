from .metamessage import MetaMessage

from pydantic import  Field

from typing import  Optional

class BaseMessage(MetaMessage):
    message_type:Optional[str] = Field(default="")

