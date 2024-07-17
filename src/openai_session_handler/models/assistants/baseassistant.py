from .metaassistant import MetaAssistant

from pydantic import  Field
from typing import  Optional, TypeVar, Type
import re

import openai.types.beta
 

from ..stream_thread import StreamThread

from ..openai_functions import describe_all_openai_functions

T = TypeVar('T', bound='BaseAssistant')


class BaseAssistant (MetaAssistant):

    assistant_type:Optional[str] = Field(default="")
    pub_thread:Optional[str] = Field(default="")



    @classmethod
    def create(cls:Type[T], **kwargs) -> T:
        kwargs['assistant_type'] = cls.__name__

        pub_thread = StreamThread.create()
        kwargs['pub_thread'] = pub_thread.id

        cls._reference_class_abc = openai.types.beta.assistant.Assistant 
        return cls.generic_create( **kwargs)
    

    @classmethod
    def delete(cls:Type[T], assistant_id):
        _a = cls.retrieve(assistant_id=assistant_id)

        StreamThread.delete(thread_id=_a.pub_thread)
        
        cls._reference_class_abc = openai.types.beta.assistant.Assistant
        return cls.generic_delete( assistant_id=assistant_id)


    def _publish(self, content:str):

        pub_thread = StreamThread.retrieve(thread_id=self.pub_thread)
        pub_thread.publish_message(content=content)



    def add_item_to_composite_field(self, item_id, composite_field_name):
        sqlish_stmt = f"ADD {item_id} TO {composite_field_name}"
        self._publish(content=sqlish_stmt)
        



    def create_list_item(self, list_type,  list_id:str):
        sqlish_stmt = f"CREATE {list_type} IDENTIFIED BY {list_id}"
        self._publish(content=sqlish_stmt)
    

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

            if self.is_custom_field( field_name=field_name):
                self.generic_update_metadata()
            else:
                self.generic_update()
        else:
            print(f"error in SQLish")



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


