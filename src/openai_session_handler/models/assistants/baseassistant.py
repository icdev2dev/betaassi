from .metaassistant import MetaAssistant
from ..threads.basethread import BaseThread

from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Dict, List, Optional, TypeVar, Type
import re


import openai.types.beta
 

from ..beta import  generic_create, generic_retrieve, generic_delete, generic_list_items
from ..beta import generic_update


from ..openai_functions import describe_all_openai_functions
from ..stream_thread import StreamThread
from ..session import Session
from ..client import client

T = TypeVar('T', bound='BaseAssistant')




class BaseAssistant (MetaAssistant):

    assistant_type:Optional[str] = Field(default="")

    

    @classmethod
    def create(cls:Type[T], **kwargs) -> T:
        kwargs['assistant_type'] = cls.__name__
        cls._reference_class_abc = openai.types.beta.assistant.Assistant 
        return generic_create(cls, **kwargs)
    

    @classmethod
    def retrieve(cls:Type[T], assistant_id) -> T:

        cls._custom_convert_for_retrieval = super()._custom_convert_for_retrieval
        cls._reference_class_abc = openai.types.beta.assistant.Assistant
        return generic_retrieve(cls, assistant_id=assistant_id)


    @classmethod
    def delete(cls:Type[T], assistant_id):
#        _a = cls.retrieve(assistant_id=assistant_id)

        cls._reference_class_abc = openai.types.beta.assistant.Assistant
        return generic_delete(cls=cls, assistant_id=assistant_id)

    @classmethod
    def list(cls:Type[T], **kwargs):
        cls._reference_class_abc = openai.types.beta.assistant.Assistant
        return generic_list_items(cls,"assistant_type",  **kwargs)

            

    def __init__(self, **data):
        
        if 'instructions' not in data:
            if self.__doc__ is not None:
                data['instructions'] = self.__doc__
            else:
                data['instructions'] = "NO INSTRUCTIONS IN CLASS DOC"

        super().__init__(**data)





    

    

         
class ClassedAssistant(BaseAssistant):
    assistant_class:str = Field(default=None)



class ProfessionalSentenceCreator(BaseAssistant):
    """You are a professional sentence creator. Using the sentence given to you, 
        please reword the sentence to make it sound more professional sounding 
        from the perspective of a senior product manager
    """
    pass

@describe_all_openai_functions()
class FunctionFinder(BaseAssistant):
    """ You are a function finder. You have access to a defined set of functions and the descriptions of the functions. 
        Your job is to figure out which subset of functions a specific person in a specific role will need. The set
         of functions is defined below with the name along with its description:

         # NAME : DESCRIPTION         

    """


    def __init__(self, **data):
        super().__init__(**data)
        
class StoryEditorAssistant(BaseAssistant): 
    """ You are a story editor assistant. """
    pass




if __name__ == "__main__":
#    tools = include_code_interpreter()
#    tools = include_retrieval(tools)
#    tools = include_all_openai_functions(tools)


#    ffa = FunctionFinder(name="functionFinder", tools=tools, model="gpt-3.5-turbo-1106")
#    ffa.create_assistant()

    sta = StoryEditorAssistant(name="storyEditorAssistant",  model="gpt-3.5-turbo-1106")
    sta.create_assistant()

    pta1 = ProfessionalSentenceCreator(name="lvl1_ProfessionalSentenceCreator", model="gpt-3.5-turbo-1106")
    pta2 = ProfessionalSentenceCreator(name="lvl2_ProfessionalSentenceCreator", model="gpt-4-1106-preview")


