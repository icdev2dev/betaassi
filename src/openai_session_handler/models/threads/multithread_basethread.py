import re
from typing import Optional, Type, TypeVar
from pydantic import Field

from .basethread import BaseThread
from ..stream_thread import StreamThread

from ..assistants.mtbt_threadtracker import MTBThreadTracker

T = TypeVar('T', bound='MultiThreadBaseThread')


class MultiThreadBaseThread(BaseThread):
    pub_thread:Optional[str] = Field(default="")

    @classmethod
    def create(cls:Type[T], **kwargs) -> T:
        pub_thread = StreamThread.create()
        kwargs['pub_thread'] = pub_thread.id
        

        if len(MTBThreadTracker.list()) == 0:
            thread_tracker = MTBThreadTracker.create()
        else:
            thread_tracker = MTBThreadTracker.list()[0]     ## assume one threadtraccker
        thread = super().create(**kwargs)
        thread_tracker.add_thread(thread_id=thread.id)
        return thread
    

        

    @classmethod
    def delete(cls:Type[T], thread_id) :
        current_thread = cls.retrieve(thread_id=thread_id)
        super().delete(current_thread.pub_thread)       

        if len(MTBThreadTracker.list()) == 0:
            pass
        else:
            thread_tracker = MTBThreadTracker.list()[0]
            thread_tracker.delete_thread(thread_id=thread_id)
        return super().delete(thread_id=thread_id)
    
    @classmethod
    def list(cls:Type[T]): 
        if len(MTBThreadTracker.list()) == 0:
            return []
        else:
            return MTBThreadTracker.list()[0].mtbthreads
        



    def update(self, **kwargs) :

        if len(kwargs.keys()) == 1: 
            field_name, field_value = kwargs.items()[0]
            self.set_attr(field_name, field_value)
        else: 
            raise ValueError("Only one parameter is currently supported for multithreaded basethread")


    def _publish(self, content:str):
        pub_thread = StreamThread.retrieve(thread_id=self.pub_thread)
        pub_thread.publish_message(content=content)

    def set_attr(self, field_name, field_value) :
        content = f"SET {field_name} = {field_value}"        
        self._publish(content=content)


    def _set_attr(self, sqlish:str):
        pattern = r"SET (\w+) = (.+)"
        match = re.search(pattern, sqlish)

        if match:
            field_name = match.group(1)
            field_value = match.group(2)
            self.__setattr__(field_name, field_value)
            self.generic_update_metadata()            
        else:
            print(f"error in SQLish")

