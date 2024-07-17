from .metathread import MetaThread
from typing import Optional, List
from pydantic import Field
from ..messages.basemessage import BaseMessage

from ..client import client

class BaseThread(MetaThread):
    thread_type: Optional[str] = Field(default="")   

    def list_messages(self, limit:int=20, order:str= "desc",after:str=None, before:str=None ) -> List:
        raw_items = client.beta.threads.messages.list(thread_id=self.id, limit=limit, order=order, after=after, before=before).data        
        return raw_items

    def create_message(self, content, role="user" ):
        client.beta.threads.messages.create(thread_id=self.id, content=content, role=role,)

    def delete_message(self, message_id):
        client.beta.threads.messages.delete(thread_id=self.id, message_id=message_id)


