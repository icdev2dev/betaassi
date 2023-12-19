from pydantic import BaseModel

from typing import TypeVar

from .client import client
from .assistants.baseassistant import BaseAssistant

ASSISTANT_TYPES = {
    'BaseAssistant': BaseAssistant,
}

T = TypeVar('T', bound='BaseAssistant')

class GenericAssistant(BaseModel):
    @staticmethod
    def list_assistants () :
        list_assistants = [(x.id, x.name, x.metadata['assistant_type']) for x in client.beta.assistants.list().data]
        return list_assistants
    
    @staticmethod
    def retrieve_assistant(assistant_id) -> T :
        for x in client.beta.assistants.list().data : 

            if x.id == assistant_id:

                if x.metadata['assistant_type'] in ASSISTANT_TYPES.keys():
                    return ASSISTANT_TYPES[x.metadata['assistant_type']].retrieve(x.id)
                else:
                    return None
        return None

