from typing import Optional, Dict,  Type, TypeVar
from pydantic import Field, field_validator
import json

import openai


from ..beta import Beta


from ..beta import check_metadata
from ..client import client


T = TypeVar('T', bound='MetaThread')


class MetaThread (Beta):
        # ALL fields from openai threads

    id:Optional[str] = None
    object:Optional[str] = None
    created_at: Optional[int] = None
    metadata: Dict[str,str]=Field(default={})



    _check_metadata = field_validator('metadata')(classmethod(check_metadata))
    _do_not_include_at_creation_time = ['id', 'object', 'created_at', 'assistant_id', 'run_id']
    _do_not_include_at_update_time = ['id', 'object', 'created_at']
    


    @staticmethod
    def _create_fn(**kwargs):
        return client.beta.threads.create(**kwargs)

    @staticmethod
    def _retrieve_fn(thread_id):
        return client.beta.threads.retrieve(thread_id=thread_id)

    @staticmethod 
    def _custom_convert_for_retrieval(kwargs):
        return kwargs

    @staticmethod
    def _update_fn(thread_id, **kwargs):
        return client.beta.threads.update(thread_id=thread_id, **kwargs)

    @staticmethod
    def _delete_fn(thread_id, **kwargs):
        return client.beta.threads.delete(thread_id=thread_id)
    
    @classmethod
    def create(cls:Type[T], **kwargs) -> T:
        cls._reference_class_abc = openai.types.beta.thread.Thread 
        kwargs['thread_type'] = cls.__name__

        return cls.generic_create( **kwargs)
    
    @classmethod
    def retrieve(cls:Type[T], thread_id) -> T:

        cls._custom_convert_for_retrieval = cls._custom_convert_for_retrieval
        cls._reference_class_abc = openai.types.beta.thread.Thread
        return cls.generic_retrieve( thread_id=thread_id)

    @classmethod
    def delete(cls:Type[T], thread_id) :
        cls._reference_class_abc = openai.types.beta.thread.Thread
        return cls.generic_delete( thread_id=thread_id)

    def update(self, **kwargs) :

        self.__class__._reference_class_abc = openai.types.beta.thread.Thread
        return self.generic_update( **kwargs)

    
