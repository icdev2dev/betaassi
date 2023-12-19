import typing
from typing import get_origin, get_args
from typing import Dict, Type, List
import json


from pydantic import BaseModel


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

def get_ref_fields(self):
    reference_class_abc = self.__class__._reference_class_abc
    if not isinstance(reference_class_abc, type):
        raise TypeError(f"_reference_class must be a class, got {type(reference_class_abc)}")
    ref_fields = set(reference_class_abc.__annotations__)
    return ref_fields


def get_custom_fields (self):
    
    ref_fields = get_ref_fields(self=self)

    cls_fields = set(self.dict())
 
    return list(cls_fields - ref_fields)

def is_custom_field(self, field_name) -> bool:
    if field_name in get_custom_fields(self=self):
        return True
    else:
        return False
    

def get_all_annotations(cls):
    annotations = {}
    for base_class in reversed(cls.__mro__):
        if issubclass(base_class, BaseModel) and hasattr(base_class, '__annotations__'):
            annotations.update(base_class.__annotations__)
    return annotations


def to_metadata(self) -> Dict[str, str]:
    metadata = {}
    custom_fields = get_custom_fields(self)

    for custom_field in custom_fields:
        if self.__dict__[custom_field] != None:
            metadata[custom_field] = self.__dict__[custom_field]
    return metadata


def from_metadata(self, metadata):
    
    self.metadata = metadata
    custom_fields = get_custom_fields(self)

    all_annotations = get_all_annotations(self.__class__) 
    for custom_field in custom_fields:
        if custom_field in metadata:

            field_type = all_annotations[custom_field]
            casted_value = cast_to_field_type(metadata[custom_field], field_type)
            setattr(self, custom_field, casted_value)
    return self

       



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



def generic_delete(cls, **kwargs):
    return cls._delete_fn(**kwargs)


def generic_update(self):
    ref_fields = get_ref_fields(self=self)
    ref_fields = ref_fields - set(self._do_not_include_at_update_time)  

    kwargs = {}
    for ref_field in ref_fields : 
        try :
            ref_field_value = getattr(self, ref_field)
            print(f" {ref_field}  -- > {ref_field_value}")

        except AttributeError :
            pass
        else:
            kwargs[ref_field] = ref_field_value
    print(self.id)
    print(kwargs)
    self._update_fn(self.id, **kwargs)
    
        

def generic_update_metadata(self):
    metadata = to_metadata(self=self)
    self.metadata = metadata
    self._update_fn(self.id, metadata=metadata)
    


def generic_retrieve(cls, **kwargs):

    def get_field_value(model_instance, field_name):
        return getattr(model_instance, field_name, None)

    all_annotations = get_all_annotations(cls=cls)

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

    return from_metadata(base_instance, metadata)


def generic_create(cls, **kwargs):
    base_instance = cls(**kwargs)
    metadata = to_metadata(base_instance)
    base_instance.metadata = metadata

    kwargs_from_base = {key: val for key, val in base_instance.__dict__.items()}

    custom_fields = get_custom_fields(base_instance)
    for custom_field in custom_fields:
        if custom_field in kwargs_from_base:
            del kwargs_from_base[custom_field]

    # Delete specific fields
    for field in base_instance._do_not_include_at_creation_time:
        kwargs_from_base.pop(field, None)

    oai_instance = cls._create_fn(**kwargs_from_base)

    
    base_instance.id = oai_instance.id
    base_instance.object = oai_instance.object
    base_instance.created_at = oai_instance.created_at

    return base_instance


def generic_list_items(cls, **kwargs):
    raw_items = cls._list_fn(**kwargs)
    ref_cls = cls._reference_class_abc

    processed_items = []
    for item in raw_items:
        if isinstance(item, ref_cls):
            # Convert to dict and instantiate cls
            item_dict = item.dict()
            processed_item = cls(**item_dict)
        else:
            # If item is a dictionary, instantiate ref_cls from it and then cls
            ref_instance = ref_cls(**item)
            item_dict = ref_instance.dict()
            processed_item = cls(**item_dict)
        processed_items.append(processed_item)

    return processed_items



class Beta(BaseModel):

    _list_registry : Dict[str, Type[BaseModel]] = {}


    def get_storage_attributes(self, list_type: str) -> List[str]:

        """
        Subclasses should override this method to return specific storage attributes
        for a given list_type.
        """
        raise NotImplementedError
    
    def get_serde(self, list_type: str) :

        """
        Subclasses should override this method to return serializable entitity
        for a given list_type.
        """
        raise NotImplementedError


    def update_storage(self, list_type: str, storage_values: List[str]):
        storage_attrs = self.get_storage_attributes(list_type)
        for attr, value in zip(storage_attrs, storage_values):
            setattr(self, attr, value)

    

    def save_list(self, list_type, list_items_of_type):
        _ser_list_items_of_type = [x.compact_ser() for x in list_items_of_type]
        strrep__list_items_of_type = json.dumps(_ser_list_items_of_type)
            
        if list_type in self._list_registry:
            num_storage_buckets = len(self.get_storage_attributes(list_type=list_type)) 

            max_length = 512  # maximum length for each attribute
            parts = [strrep__list_items_of_type[i:i + max_length] for i in range(0, len(strrep__list_items_of_type), max_length)]
            if len(parts) > num_storage_buckets:
                raise ValueError(f"String too long: can only store up to {len(num_storage_buckets)*max_length} characters.")

            self.update_storage(list_type=list_type, storage_values=parts)
        
        generic_update_metadata(self=self)



        
    def load_list(self, list_type):
        if list_type in self._list_registry:

            strrep__list_items_of_type =  ''.join([getattr(self, x) for x in self.get_storage_attributes(list_type=list_type)])
        

            if len(strrep__list_items_of_type) != 0: 

                json_loads = json.loads(strrep__list_items_of_type)
                ret_list = []

                for x in json_loads:
                    serde_class = self.get_serde(list_type=list_type)

                    serde_instance = serde_class.compact_deser(x)

                    serde_instance_class = serde_class.model_validate_json(json.dumps(serde_instance) )
                    ret_list.append(serde_instance_class)
                    
                return ret_list
            else: 
                return []

