
OPENAI_TYPE_MAP = {
    'str': "string",
    'int': "integer",
    'List': 'array'
}


def openai_function(openai_functions): 
    def wrapper(func):

        function = dict()
        function['name'] = func.__name__
        function['description'] = func.__doc__
        function['parameters'] = {}
        function['parameters']['type'] = "object"
        function['parameters']['properties'] = {}

        

        input_arg_names = [arg_name for arg_name in func.__code__.co_varnames[:func.__code__.co_argcount]]

        for input_arg_name in input_arg_names:
            function['parameters']['properties'][input_arg_name] = {}
            raw_annotation = func.__annotations__[input_arg_name]


            if raw_annotation.__origin__.__name__ in OPENAI_TYPE_MAP:
                ip_type = OPENAI_TYPE_MAP[raw_annotation.__origin__.__name__]
                function['parameters']['properties'][input_arg_name]['type'] = ip_type

                if ip_type == 'array':
                    function['parameters']['properties'][input_arg_name]['items'] = {}
                    ip_item_type = raw_annotation.__origin__.__args__[0].__name__
                    if ip_item_type in OPENAI_TYPE_MAP:
                        function['parameters']['properties'][input_arg_name]['items']['type'] = OPENAI_TYPE_MAP[ip_item_type]
                    else:
                        function['parameters']['properties'][input_arg_name]['items']['type'] = ip_item_type

            else:
                ip_type =  raw_annotation.__origin__.__name__
                function['parameters']['properties'][input_arg_name]['type'] = ip_type


            function['parameters']['properties'][input_arg_name]['type'] = ip_type
            function['parameters']['properties'][input_arg_name]['description'] = raw_annotation.__metadata__[0]

        openai_functions.append(function)

        return func
    return wrapper

