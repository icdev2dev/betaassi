from ..beta import Beta
from pydantic import Field, field_validator
import openai

from ..beta import check_metadata

from typing import List, Dict, Optional, TypeVar, Type

from ..client import client

T = TypeVar('T', bound='MetaMessage')


class MetaMessage(Beta):

    id:Optional[str] = None
    object:Optional[str] = None
    created_at: Optional[int] = None
    metadata: Dict[str,str]=Field(default={})

    thread_id: str = Field(...)
    role:str = Field(...)
    content: List[Dict] = Field(...)

    assistant_id: Optional[str] = Field(default="")
    run_id: Optional[str] = Field(default="")
    
#    file_ids: Optional[List[str]] = Field(default=None)


    _check_metadata = field_validator('metadata')(classmethod(check_metadata))

    _do_not_include_at_creation_time = ['id', 'object', 'created_at', 'assistant_id', 'run_id']
    _do_not_include_at_update_time = ['id', 'object', 'created_at',  "role", "content",  "file_ids", 'assistant_id', 'run_id']
    _custom_field_conversion_at_update_time = [['thread_id', "thread_id"]]


    @staticmethod
    def _create_fn( **kwargs):

        thread_id = kwargs.pop("thread_id")

        
        if thread_id:

            kwargs = {key:val for key, val in kwargs.items() if val != None or val != ""}


            if 'content' in kwargs:
                content = kwargs['content'][0]['text']['value']
                kwargs['content'] = content

            if 'role' not in kwargs:
                kwargs['role'] = 'user'            

#            print(thread_id)
#            print(kwargs)
            
            return client.beta.threads.messages.create(thread_id, **kwargs)
        else: 
            raise ValueError("No thread id specfied in create")
        

    @staticmethod
    def _retrieve_fn(thread_id, message_id):
        return client.beta.threads.messages.retrieve(thread_id=thread_id, message_id=message_id)

    @staticmethod 
    def _custom_convert_for_retrieval(kwargs):
        kwargs['content'] = [{'type': x.type, 'annotations': getattr(x, x.type).annotations, 'value':getattr(x, x.type).value  } for x in kwargs['content']]
        return kwargs
        
    @staticmethod
    def _update_fn(message_id, **kwargs):

        return client.beta.threads.messages.update(message_id=message_id, **kwargs)

    @staticmethod
    def _list_fn(**kwargs):
        return client.beta.threads.messages.list(**kwargs)
    

    @classmethod
    def create(cls:Type[T], **kwargs) -> T:

    
        if 'content' in kwargs.keys():
            content = kwargs['content']
            kwargs['content'] = [{'type': 'text', 'text': {'annotations': [], 'value': content}}]
#            print( kwargs['content'])
        else:
            kwargs['content'] = [{'type': 'text', 'text': {'annotations': [], 'value': ''}}]

        kwargs['message_type'] = cls.__name__
        
        cls._reference_class_abc = openai.types.beta.threads.thread_message.ThreadMessage 
        return cls.generic_create( **kwargs)
    
    @classmethod
    def retrieve(cls:Type[T], thread_id, message_id) -> T:
        cls._custom_convert_for_retrieval = cls._custom_convert_for_retrieval
        cls._reference_class_abc = openai.types.beta.threads.thread_message.ThreadMessage
        return cls.generic_retrieve( thread_id=thread_id, message_id=message_id)

    @classmethod
    def list(cls, **kwargs):
        cls._reference_class_abc = openai.types.beta.threads.thread_message.ThreadMessage
        return cls.generic_list_items( 'message_type', **kwargs)



    def update(self, **kwargs) :
        self.__class__._reference_class_abc = openai.types.beta.threads.thread_message.ThreadMessage
        return self.generic_update( **kwargs)
    
    