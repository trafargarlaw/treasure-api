
from email_validator import validate_email
from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing_extensions import TypedDict

CUSTOM_VALIDATION_ERROR_MESSAGES = {
    "arguments_type": "Invalid argument type",
    "assertion_error": "Assertion error",
    "bool_parsing": "Boolean parsing error",
    "bool_type": "Invalid boolean type",
    "bytes_too_long": "Bytes too long",
    "bytes_too_short": "Bytes too short",
    "bytes_type": "Invalid bytes type",
    "callable_type": "Invalid callable type",
    "dataclass_exact_type": "Invalid dataclass instance type",
    "dataclass_type": "Invalid dataclass type",
    "date_from_datetime_inexact": "Non-zero date components",
    "date_from_datetime_parsing": "Date parsing error",
    "date_future": "Date must be in the future",
    "date_parsing": "Date validation error",
    "date_past": "Date must be in the past",
    "date_type": "Invalid date type",
    "datetime_future": "Datetime must be in the future",
    "datetime_object_invalid": "Invalid datetime object",
    "datetime_parsing": "Datetime parsing error",
    "datetime_past": "Datetime must be in the past",
    "datetime_type": "Invalid datetime type",
    "decimal_max_digits": "Too many decimal digits",
    "decimal_max_places": "Invalid decimal places",
    "decimal_parsing": "Decimal parsing error",
    "decimal_type": "Invalid decimal type",
    "decimal_whole_digits": "Invalid decimal digits",
    "dict_type": "Invalid dictionary type",
    "enum": "Invalid enum member, allowed values: {expected}",
    "extra_forbidden": "Extra fields not permitted",
    "finite_number": "Invalid finite number",
    "float_parsing": "Float parsing error",
    "float_type": "Invalid float type",
    "frozen_field": "Frozen field error",
    "frozen_instance": "Frozen instance cannot be modified",
    "frozen_set_type": "Frozen type not allowed",
    "get_attribute_error": "Attribute error",
    "greater_than": "Value too large",
    "greater_than_equal": "Value too large or equal",
    "int_from_float": "Invalid integer type",
    "int_parsing": "Integer parsing error",
    "int_parsing_size": "Integer parsing size error",
    "int_type": "Invalid integer type",
    "invalid_key": "Invalid key",
    "is_instance_of": "Invalid type instance",
    "is_subclass_of": "Invalid type subclass",
    "iterable_type": "Invalid iterable type",
    "iteration_error": "Iteration error",
    "json_invalid": "Invalid JSON string",
    "json_type": "Invalid JSON type",
    "less_than": "Value too small",
    "less_than_equal": "Value too small or equal",
    "list_type": "Invalid list type",
    "literal_error": "Invalid literal value",
    "mapping_type": "Invalid mapping type",
    "missing": "Required field missing",
    "missing_argument": "Missing argument",
    "missing_keyword_only_argument": "Missing keyword argument",
    "missing_positional_only_argument": "Missing positional argument",
    "model_attributes_type": "Invalid model attributes type",
    "model_type": "Invalid model instance",
    "multiple_argument_values": "Too many argument values",
    "multiple_of": "Value must be multiple of",
    "no_such_attribute": "Invalid attribute assignment",
    "none_required": "Value must be None",
    "recursion_loop": "Recursive assignment",
    "set_type": "Invalid set type",
    "string_pattern_mismatch": "String pattern mismatch",
    "string_sub_type": "Invalid string subtype (non-strict instance)",
    "string_too_long": "String too long",
    "string_too_short": "String too short",
    "string_type": "Invalid string type",
    "string_unicode": "String must be Unicode",
    "time_delta_parsing": "Timedelta parsing error",
    "time_delta_type": "Invalid timedelta type",
    "time_parsing": "Time parsing error",
    "time_type": "Invalid time type",
    "timezone_aware": "Missing timezone information",
    "timezone_naive": "Timezone information not allowed",
    "too_long": "Too long",
    "too_short": "Too short",
    "tuple_type": "Invalid tuple type",
    "unexpected_keyword_argument": "Unexpected keyword argument",
    "unexpected_positional_argument": "Unexpected positional argument",
    "union_tag_invalid": "Invalid union type literal",
    "union_tag_not_found": "Union type parameter not found",
    "url_parsing": "URL parsing error",
    "url_scheme": "Invalid URL scheme",
    "url_syntax_violation": "URL syntax violation",
    "url_too_long": "URL too long",
    "url_type": "Invalid URL type",
    "uuid_parsing": "UUID parsing error",
    "uuid_type": "Invalid UUID type",
    "uuid_version": "Invalid UUID version",
    "value_error": "Value error",
}

CUSTOM_USAGE_ERROR_MESSAGES = {
    "class-not-fully-defined": "Class attributes not fully defined",
    "custom-json-schema": "__modify_schema__ method deprecated in V2",
    "decorator-missing-field": "Invalid field validator defined",
    "discriminator-no-field": "Discriminator fields not fully defined",
    "discriminator-alias-type": "Discriminator field using non-string type",
    "discriminator-needs-literal": "Discriminator field requires literal value",
    "discriminator-alias": "Inconsistent discriminator field alias",
    "discriminator-validator": "Field validators not allowed for discriminator",
    "model-field-overridden": "Cannot override field without type definition",
    "model-field-missing-annotation": "Missing field type annotation",
    "config-both": "Duplicate config definition",
    "removed-kwargs": "Removed keyword config parameter called",
    "invalid-for-json-schema": "Invalid JSON type exists",
    "base-model-instantiated": "Base model cannot be instantiated",
    "undefined-annotation": "Missing type annotation",
    "schema-for-unknown-type": "Unknown type definition",
    "create-model-field-definitions": "Field definition error",
    "create-model-config-base": "Config definition error",
    "validator-no-fields": "No fields specified for validator",
    "validator-invalid-fields": "Invalid validator field definition",
    "validator-instance-method": "Validator must be class method",
    "model-serializer-instance-method": "Serializer must be instance method",
    "validator-v1-signature": "V1 validator error deprecated",
    "validator-signature": "Invalid validator signature",
    "field-serializer-signature": "Unrecognized field serializer signature",
    "model-serializer-signature": "Unrecognized model serializer signature",
    "multiple-field-serializers": "Duplicate field serializer definition",
    "invalid_annotated_type": "Invalid type annotation",
    "type-adapter-config-unused": "Invalid type adapter config",
    "root-model-extra": "Extra fields not allowed in root model",
}


class SchemaBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)


class CustomPhoneNumber(PhoneNumber):
    default_region_code = "MA"


class CustomEmailStr(EmailStr):
    @classmethod
    def _validate(cls, __input_value: str) -> str:
        if __input_value == "":
            return ""
        return str(validate_email(__input_value).normalized)


class PhoneNumbersJSON(TypedDict, total=False):
    mobile: list[CustomPhoneNumber] | None
    home: list[CustomPhoneNumber] | None
    fax: list[CustomPhoneNumber] | None


class AddressStructure(TypedDict, total=False):
    address: str
    city_id: int
    country_id: int
    postal_code: str


class AddressJSON(TypedDict, total=False):
    ar: AddressStructure
    lat: AddressStructure
