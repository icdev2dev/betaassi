from pydantic import Field

from .basemessage import BaseMessage


class StreamMessage(BaseMessage) :
    sm_status:str = Field(default="")

    @classmethod
    def publish_message(cls, thread_id, content:str) :
        cls.create(thread_id=thread_id, role="user", sm_status="created", content=content)


    
    

