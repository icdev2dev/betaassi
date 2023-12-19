
from openai import OpenAI
from typing import Annotated, List, Dict
import uuid

from .openai_functions_utils import openai_function

SP_CLIENT = OpenAI()

OPENAI_FUNCTIONS = []
ASSISTANT_NAME_REGISTRY = {
    'AbcAssistant': 'abc'
}

def describe_all_openai_functions() :
    def deco(cls):
        desc=""
        for openai_function in OPENAI_FUNCTIONS:
            desc += f"# {openai_function['name']} : {openai_function['description']} \n"
        if (cls.__doc__) :
            cls.__doc__ += desc
        else:
            cls.__doc__ = desc
        return cls
    return deco


def auto_init_assistant(cls):

    original_init = cls.__init__

    def new_init(self, **data):

        data.setdefault('metadata', {'cid': uuid.uuid4().hex})
        if 'cname' in data:
            data['name'] = data['cname']
            data['metadata'].update({'cname': data.pop('cname')})

        if self.__class__.__name__ in ASSISTANT_NAME_REGISTRY:
            data['metadata'].update({'ctype': ASSISTANT_NAME_REGISTRY[self.__class__.__name__]})
        else:
            if 'ctype' in data: 
                data['metadata'].update({'ctype': data.pop('ctype')})
            else: 
                data['metadata'].update({'ctype': 'unknown'})

        original_init(self, **data)

    cls.__init__ = new_init
    return cls


def include_code_interpreter(ret_val=[]) -> List[Dict]:
    ret_val.append({
        "type": "code_interpreter"
    })
    return ret_val

def include_retrieval(ret_val=[]) -> List[Dict]:
    ret_val.append({
        "type": "retrieval"
    })
    return ret_val

def include_all_openai_functions(ret_val=[])-> List[Dict] :

    for openai_function in OPENAI_FUNCTIONS:
        
        ret_val.append( {
            "type": "function", 
            "function": openai_function
        })

    return ret_val




@openai_function(OPENAI_FUNCTIONS)
def get_weather(city: Annotated[str, "City in US"], state: Annotated[str, "State in US"]) -> str :
    """This function gets the weather of a city given a state in the United States."""
    return (f"weather in {city}, {state} is good")


@openai_function(OPENAI_FUNCTIONS)
def get_average_rainfall(city: Annotated[str, "City in US"], state: Annotated[str, "State in US"]) -> str :
    """This function gets the average annual rainfall of a city given a state in the United States."""
    return (f"average rainfall in {city}, {state} is 36 inches.")


@openai_function(OPENAI_FUNCTIONS)
def get_comments_in_git_commit(git_commit: Annotated[str, "the git commit"]) -> str :
    """This function gets the comments in a specific git commit"""
    return (f"Modified dev something")

@openai_function(OPENAI_FUNCTIONS)
def provide_name(name:Annotated[str, "the name"]):
    """This function provides a name given a role description"""
    pass

@openai_function(OPENAI_FUNCTIONS)

def provide_functions(funcs:Annotated[List[str], "The subset of functions appropriate for the given role"]):
    """This function provides the subset of functions for a given role"""
    pass

