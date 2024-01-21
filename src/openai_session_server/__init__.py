from openai_session_server.server import run_main, _add_registered_assistant, _rm_registered_assistant



def run_server() :
    run_main()
    pass


def add_registered_assistant(assistant):
    _add_registered_assistant(registered_assistant_class=assistant)
    