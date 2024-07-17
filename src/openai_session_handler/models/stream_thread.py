from pydantic import Field

from typing import List

from .threads.basethread import BaseThread
from .messages.streammessage import StreamMessage

from .client import client


class StreamThread (BaseThread):

    hwm:str = Field(default="")

    def publish_message(self, content:str) :
        StreamMessage.publish_message(thread_id=self.id, content=content)


    def list_messages(self, limit:int=20, order:str= "desc",after:str=None, before:str=None ) -> List[StreamMessage]:
        raw_items = client.beta.threads.messages.list(thread_id=self.id, limit=limit, order=order, after=after, before=before).data        
        processed_items = [StreamMessage.retrieve(thread_id=self.id, message_id = item.id)  for item in raw_items]
        return processed_items


    def set_hwm (self, hwm: str) :
        self.hwm = hwm
        self.generic_update_metadata()

    def _reset_hwm(self):
        """ only for experimentation"""
        self.hwm = ""
        
        self.generic_update_metadata()

