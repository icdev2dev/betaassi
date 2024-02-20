
from ..beta import Beta, check_metadata
from pydantic import Field, field_validator
from typing import  Optional, Dict, Type, TypeVar, List
from ..client import client



import openai



T = TypeVar('T', bound='MetaAssistant')


class MetaAssistant(Beta):
    
    # ALL FIELDS FROM OPENAI ASSISTANT
    id:Optional[str] = None
    object:Optional[str] = None
    created_at: Optional[int] = None
    metadata: Dict[str,str]=Field(default={})


    name: str = Field(default="ABC", max_length=512)
    description: str = Field(default="Default Description", max_length=512)
    instructions: str = Field(...)
    
    model:str = Field(default="gpt-4", max_length=512)    
    
#    tools: Optional[List[Dict]] = Field(default=None)
#    file_ids: Optional[List[str]] = Field(default=None)



    _check_metadata = field_validator('metadata')(classmethod(check_metadata))
    _do_not_include_at_creation_time = ['id', 'object', 'created_at']
    _do_not_include_at_update_time = ['id', 'object', 'created_at']


    # ALL OPEN AI CRUDL Functions MUST BE DEFINED HERE

    @staticmethod
    def _create_fn(**kwargs):
        return client.beta.assistants.create(**kwargs)

    @staticmethod
    def _retrieve_fn(assistant_id):
        return client.beta.assistants.retrieve(assistant_id=assistant_id)
    
    @staticmethod  
    def _custom_convert_for_retrieval(kwargs):
        return kwargs

    @staticmethod
    def _update_fn(assistant_id, **kwargs):
        return client.beta.assistants.update(assistant_id=assistant_id, **kwargs)

    @staticmethod
    def _delete_fn(assistant_id):
        return client.beta.assistants.delete(assistant_id=assistant_id)
    
    @staticmethod
    def _list_fn(**kwargs):
        return client.beta.assistants.list(**kwargs)



    @classmethod
    def create(cls:Type[T], **kwargs) -> T:
        cls._reference_class_abc = openai.types.beta.assistant.Assistant 
        return cls.generic_create(**kwargs)
    

    @classmethod
    def retrieve(cls:Type[T], assistant_id) -> T:

        cls._custom_convert_for_retrieval = cls._custom_convert_for_retrieval
        cls._reference_class_abc = openai.types.beta.assistant.Assistant
        return cls.generic_retrieve( assistant_id=assistant_id)


    @classmethod
    def delete(cls:Type[T], assistant_id):
        cls._reference_class_abc = openai.types.beta.assistant.Assistant
        return cls.generic_delete( assistant_id=assistant_id)


    @classmethod
    def list(cls:Type[T], **kwargs) -> List[T]:
        cls._reference_class_abc = openai.types.beta.assistant.Assistant
        return cls.generic_list_items("assistant_type",  **kwargs)


    def update(self, **kwargs) :
        self.__class__._reference_class_abc = openai.types.beta.assistant.Assistant
        return self.generic_update( **kwargs)
    
    

    def __init__(self, **data):
        
        if 'instructions' not in data:
            if self.__doc__ is not None:
                data['instructions'] = self.__doc__
            else:
                data['instructions'] = "NO INSTRUCTIONS IN CLASS DOC"

        super().__init__(**data)



