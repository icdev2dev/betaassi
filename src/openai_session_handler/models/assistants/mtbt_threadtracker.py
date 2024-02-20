from .baseassistant import BaseAssistant
from pydantic import Field, BaseModel, model_serializer
from ..beta import register_composite_fields_and_type
from typing import List, Dict
import json

class Thread(BaseModel): 
    thread_id:str = Field(...)

    @model_serializer
    def compact_ser(self) -> str:
        return json.dumps([self.thread_id])

    @staticmethod
    def compact_deser(string: str) -> Dict :
        list_fields = json.loads(string)
        return {
            'thread_id': list_fields[0]
        }





class MTBThreadTracker(BaseAssistant):
    mtbthreads_1:str = Field(default="")
    mtbthreads_2:str = Field(default="")
    mtbthreads_3:str = Field(default="")
    mtbthreads_4:str = Field(default="")

    register_composite_fields_and_type("mtbthreads", ["mtbthreads_1", "mtbthreads_2", "mtbthreads_3", "mtbthreads_4" ], Thread)

    @property
    def mtbthreads(self) -> List[Thread]:
        return self.get_composite_field('mtbthreads')
    

    def add_thread(self, thread_id):

        thread_list = self.mtbthreads
        thread_instance = Thread(thread_id=thread_id)
        thread_list.append(thread_instance)
        self.save_composite_field('mtbthreads', thread_list)


    def delete_thread(self, thread_id):
        thread_list = self.mtbthreads
        thread_list_updated = []

        for thread in thread_list:
            if thread.thread_id == thread_id:
                pass
            else:
                thread_list_updated.append(thread)

        self.save_composite_field('mtbthreads', thread_list_updated)

