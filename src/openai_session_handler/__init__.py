from .models.genericassistant import GenericAssistant

def list_assistants() :
    return GenericAssistant.list_assistants()

def  retrieve_assistant(assistant_id) :
    return GenericAssistant.retrieve_assistant(assistant_id=assistant_id)


def list_assistants_by_type(assistant_type) :
    return GenericAssistant.list_assistants_by_type(assistant_type=assistant_type)

