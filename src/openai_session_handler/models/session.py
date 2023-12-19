import json
from typing import Dict
from pydantic import BaseModel, Field, model_serializer

from .threads.basethread import BaseThread

class Session(BaseModel):
    assistant_id:str = Field(...)
    session_id: str = Field(...)
    main_thread: str = Field(...)
    interaction_thread:str = Field(...)
    session_type: str = Field(default="d", description="one letter abbr for d:default, o:oneshot, m:manyshots")
    session_type_param : str = Field(default="")
    session_model: str = Field(default="")
    last_touched: str = Field(default="")

    @model_serializer
    def compact_ser(self) -> str:
        return json.dumps([self.assistant_id,self.session_id, self.main_thread, self.interaction_thread,  self.session_type, self.session_type_param, self.session_model, self.last_touched])
    
    @staticmethod
    def compact_deser( string:str)-> Dict:
        list_fields = json.loads(string) 
        return {
            'assistant_id': list_fields[0],
            'session_id': list_fields[1],
            'main_thread': list_fields[2],
            'interaction_thread': list_fields[3],
            'session_type': list_fields[4],
            'session_type_param': list_fields[5],
            'session_model': list_fields[6],
            'last_touched': list_fields[7]
        }
    
    
    def model_dump_json(self) -> str:
        return self.compact_ser()       
        #return super().model_dump_json(indent=indent, include=include, exclude=exclude, by_alias=by_alias, exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none, round_trip=round_trip, warnings=warnings)
    
    def request_response(self, content):
        thread = BaseThread.retrieve(thread_id=self.main_thread)
        thread.request_response(assistant_id=self.assistant_id, session_id=self.session_id,  content=content)
        return {'status': 'ok'}
    
    def response_to_request(self): 
        thread = BaseThread.retrieve(thread_id=self.main_thread)
        return thread.response_to_request(assistant_id=self.assistant_id, session_id=self.session_id)

    @classmethod
    def create_session_from_string(cls, string):
        return Session.model_validate_json(json.dumps(Session.compact_deser(string=string)))
    