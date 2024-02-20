from .metaassistant import MetaAssistant

from pydantic import  Field
from typing import  Optional, TypeVar, Type

import openai.types.beta
 


from ..openai_functions import describe_all_openai_functions

T = TypeVar('T', bound='BaseAssistant')




class BaseAssistant (MetaAssistant):

    assistant_type:Optional[str] = Field(default="")

    

    @classmethod
    def create(cls:Type[T], **kwargs) -> T:
        kwargs['assistant_type'] = cls.__name__
        cls._reference_class_abc = openai.types.beta.assistant.Assistant 
        return cls.generic_create( **kwargs)
    





            

  




    

    

         
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


