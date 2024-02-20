import typing
from typing import get_origin, get_args
from typing import Dict, Type, List
import json
import re


from pydantic import BaseModel, root_validator

MAX_LENGTH_OF_METADATA_ATTRIBUTES = 512


# Unfortunately these need to be global because there is some funky behaviour with private var in pydantic

LIST_REGISTRY : Dict[str, Type[BaseModel]] = {}
COMPOSITE_FIELDS:Dict[str, List[str]] = {}


def check_metadata(cls, v):
    '''Check on metdata according to the recent documentation on openai'''
    if len(v) > 16:
        raise ValueError('Dictionary must have a maximum of 16 key-value pairs')

    for key, value in v.items():
        if len(key) > 64:
            raise ValueError('Keys must be a maximum of 64 characters')
        if len(value) > 512:
            raise ValueError('Values must be a maximum of 512 characters')
    return v


def register_composite_fields_and_type( composite_field:str, component_fields:List[str],  component_model: Type[BaseModel]):



    if composite_field not in LIST_REGISTRY.keys():
        LIST_REGISTRY[composite_field] = component_model
        COMPOSITE_FIELDS[composite_field] = component_fields
#        print(COMPOSITE_FIELDS)
#        print(LIST_REGISTRY)
    else:
        raise Exception(f"{composite_field} already exists in Registry")



       



def cast_to_field_type(value, field_type):
    origin_type = get_origin(field_type)
    args = get_args(field_type)

    # Handle Optional types
    if origin_type is typing.Union and type(None) in args:
        if value is None:
            return None
        # Remove NoneType and get the actual type
        target_type = next(arg for arg in args if arg is not type(None))
        return cast_to_field_type(value, target_type)

    # Handle List types
    elif origin_type is list or origin_type is List:
        if not isinstance(value, list):
            raise ValueError(f"Expected list for {field_type}, got {type(value)}")
        item_type = args[0]
        return [cast_to_field_type(item, item_type) for item in value]

    # Handle Dict types
    elif origin_type is dict or origin_type is Dict:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise ValueError(f"String value for {field_type} is not valid JSON")
        if not isinstance(value, dict):
            raise ValueError(f"Expected dict for {field_type}, got {type(value)}")
        return value  # Assuming the dict doesn't need further type conversions

    # Direct casting for basic types
    else:
        try:
            return field_type(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Cannot cast {value} to {field_type}: {e}")


        

    
class Beta(BaseModel):
 

    @root_validator(pre=True)
    def split_composite_fields(cls, values):

        

        for composite_field, component_fields in COMPOSITE_FIELDS.items():
            composite_value = values.pop(composite_field, None)

            if composite_value:
                # so now all that we have to do is to update the values with the values in component_fields

                num_component_fields = len(component_fields)

                compact_ser_composite_value = [x.compact_ser() for x in composite_value]
                strrep_compact_ser_composite_value = json.dumps(compact_ser_composite_value)

                parts = [strrep_compact_ser_composite_value[i:i + MAX_LENGTH_OF_METADATA_ATTRIBUTES] for i in range(0, len(strrep_compact_ser_composite_value), MAX_LENGTH_OF_METADATA_ATTRIBUTES)]

                if len(parts) > num_component_fields:
                      raise ValueError(f"String too long: can only store up to {len(num_component_fields)*MAX_LENGTH_OF_METADATA_ATTRIBUTES} characters.")
                else : 
                    for i, part in enumerate(parts):
                        values.update({component_fields[i]: part})
        
                values.update()                

        return values


    @classmethod
    def generic_create(cls, **kwargs):

        vals_popped = {}

        pattern = r"^_.*"

        for field_name, field_value in kwargs.items():
            m = re.match(pattern=pattern, string=field_name)
            if m: 
                vals_popped[field_name] = field_value
        
        for field_name in vals_popped.keys():
            kwargs.pop(field_name)


        base_instance = cls(**kwargs)


        metadata = base_instance.to_metadata()
        base_instance.metadata = metadata

        kwargs_from_base = {key: val for key, val in base_instance.__dict__.items()}

        custom_fields = base_instance.get_custom_fields()
        for custom_field in custom_fields:
            if custom_field in kwargs_from_base:
                del kwargs_from_base[custom_field]

        # Delete specific fields
        for field in base_instance._do_not_include_at_creation_time:
            kwargs_from_base.pop(field, None)


        if len(vals_popped) > 0:
            args  = []

            for item in sorted(vals_popped):
                args.append(vals_popped[item])

            oai_instance = cls._create_fn(*args, **kwargs_from_base)
        else:

            oai_instance = cls._create_fn(**kwargs_from_base)

        
        base_instance.id = oai_instance.id
        base_instance.object = oai_instance.object
        base_instance.created_at = oai_instance.created_at

        return base_instance



    @classmethod
    def generic_list_items(cls,cls_type, **kwargs):
        raw_items = cls._list_fn(**kwargs)
        ref_cls = cls._reference_class_abc

        processed_items = []
        for item in raw_items:

            if isinstance(item, ref_cls):
                # Convert to dict and instantiate cls

                item_dict = item.dict()
                
                metadata = item_dict['metadata']
                base_instance = cls(**item_dict)

                processed_item =  base_instance.from_metadata( metadata)

                if getattr(processed_item, cls_type) == cls.__name__ :
                    processed_items.append(processed_item)



            else:
                # If item is a dictionary, instantiate ref_cls from it and then cls
                print("IT IS NOT")

                ref_instance = ref_cls(**item)
                item_dict = ref_instance.dict()
                processed_item = cls(**item_dict)
                processed_items.append(processed_item)

            
        return processed_items


    @classmethod
    def generic_retrieve(cls, **kwargs):

        def get_field_value(model_instance, field_name):
            return getattr(model_instance, field_name, None)

        all_annotations = cls.get_all_annotations()

        cls_fields = set(all_annotations)
        retrieved_data = cls._retrieve_fn(**kwargs)

        metadata = retrieved_data.metadata

        kwargs = {}

        for key in cls_fields: 
            val = get_field_value(retrieved_data, key)
            if val != None:
                kwargs[key] = val
        

        kwargs = cls._custom_convert_for_retrieval(kwargs)    

        base_instance = cls(**kwargs)

        return base_instance.from_metadata( metadata)



    @classmethod
    def generic_delete(cls, **kwargs):
        return cls._delete_fn(**kwargs)


    def generic_update(self, **kwargs):


        ref_fields = self.get_ref_fields()
        ref_fields = ref_fields - set(self._do_not_include_at_update_time)  

        custom_fields = self.get_custom_fields()

        metadata = self.metadata

        kwargs_out = {}

        metadata_set = False

        for key, value in kwargs.items():
            if key in ref_fields:
                setattr(self, key, value)
                kwargs_out[key] = value

            elif key in custom_fields:
                metadata[key] = value
                setattr(self, key, value)
                metadata_set = True

        if metadata_set:
            kwargs_out['metadata'] = metadata

        if hasattr(self, '_custom_field_conversion_at_update_time'): 
            custom_field_conversion = getattr(self, '_custom_field_conversion_at_update_time')
            kwargs_out[custom_field_conversion[0][1]] = getattr(self, custom_field_conversion[0][0])



        self._update_fn(self.id, **kwargs_out)
        





    def get_composite_value(self, composite_field):
        components = COMPOSITE_FIELDS.get(composite_field, [])
        return ''.join([getattr(self, field, '') for field in components])
    
    def get_composite_field(self, composite_field):
         
         composite_value = self.get_composite_value(composite_field)

         if composite_value == "":
             return []
         else:
            j_composite_value = json.loads(composite_value )

            serde_model = LIST_REGISTRY[composite_field]

            l_c = [serde_model.model_validate_json(json.dumps(serde_model.compact_deser(x))) for x in j_composite_value]

            return l_c
    


    
    def save_composite_field(self, composite_field, list_items):

        if composite_field in LIST_REGISTRY:
            ser_list_items = [ x.compact_ser() for x in list_items]
            strrep_list_items = json.dumps(ser_list_items)

            num_storage_buckets = len(COMPOSITE_FIELDS[composite_field])


            max_length = 512  # maximum length for each attribute
            parts = [strrep_list_items[i:i + max_length] for i in range(0, len(strrep_list_items), max_length)]
            if len(parts) > num_storage_buckets:
                raise ValueError(f"String too long: can only store up to {len(num_storage_buckets)*max_length} characters.")

            for attr,value in zip(COMPOSITE_FIELDS[composite_field], parts):
                setattr(self, attr, value)

            self.generic_update_metadata()
        else:
            raise ValueError(f"{composite_field} is NOT registered in LIST_REGISTRY")
            

    def get_ref_fields(self):
        reference_class_abc = self.__class__._reference_class_abc
        if not isinstance(reference_class_abc, type):
            raise TypeError(f"_reference_class must be a class, got {type(reference_class_abc)}")
        ref_fields = set(reference_class_abc.__annotations__)
        return ref_fields

    def is_composite_field(self, field_name):
        if field_name in COMPOSITE_FIELDS.keys():
            return True
        else:
            return False


    def get_composite_field_attributes(self, field_name) -> List[str]:
        return COMPOSITE_FIELDS[field_name]


    def get_custom_fields (self):
        
        ref_fields = self.get_ref_fields()
        cls_fields = set(self.dict())
        return list(cls_fields - ref_fields)

    def is_custom_field(self, field_name) -> bool:
        if field_name in self.get_custom_fields():
            return True
        else:
            return False
        
    @classmethod
    def get_all_annotations(cls):
        annotations = {}
        for base_class in reversed(cls.__mro__):
            if issubclass(base_class, BaseModel) and hasattr(base_class, '__annotations__'):
                annotations.update(base_class.__annotations__)
        return annotations


    def to_metadata(self) -> Dict[str, str]:
        metadata = {}
        custom_fields = self.get_custom_fields()

        for custom_field in custom_fields:
            if self.__dict__[custom_field] != None:
                metadata[custom_field] = self.__dict__[custom_field]
        return metadata


    def from_metadata(self, metadata):
        
        self.metadata = metadata
        custom_fields = self.get_custom_fields()

        all_annotations = self.__class__.get_all_annotations() 

        for custom_field in custom_fields:
            if custom_field in metadata:

                field_type = all_annotations[custom_field]
                casted_value = cast_to_field_type(metadata[custom_field], field_type)
                setattr(self, custom_field, casted_value)
        return self

    def generic_update_metadata(self):
        metadata = self.to_metadata()
        self.metadata = metadata
        self._update_fn(self.id, metadata=metadata)



