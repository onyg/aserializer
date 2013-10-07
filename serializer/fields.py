# -*- coding: utf-8 -*-

import logging
import uuid

#from validators import (SerializerValidatorError,
#                        VALIDATORS_EMPTY_VALUES,
#                        validate_integer,)
import validators
logger = logging.getLogger(__name__)



class SerializerFieldValueError(Exception):

    def __init__(self, message):
        if isinstance(message, dict):
            self.error_dict = message
        elif isinstance(message, list):
            self.error_list = message
        else:
            self.message = message

    @property
    def message_dict(self):
        message_dict = {}
        for field, messages in self.error_dict.items():
            message_dict[field] = []
            for message in messages:
                if isinstance(message, SerializerFieldValueError):
                    message_dict[field].extend(message.messages)
                else:
                    message_dict[field].append(str(message))
        return message_dict

    @property
    def messages(self):
        if hasattr(self, 'error_dict'):
            message_list = self.error_dict.values()
        else:
            message_list = self.error_list

        messages = []
        for message in message_list:
            if isinstance(message, SerializerFieldValueError):
                params = message.params
                message = message.message
                if params:
                    message %= params
            message = str(message)
            messages.append(message)
        if len(messages) > 0 and isinstance(messages[0], basestring):
            return str(messages[0])
        return messages

    def __str__(self):
        if hasattr(self, 'error_dict'):
            return repr(self.message_dict)
        return repr(self.messages)

    def __repr__(self):
        return 'SerializerFieldValueError {}'.format(str(self.messages))

    def update_error_dict(self, error_dict):
        if hasattr(self, 'error_dict'):
            if error_dict:
                for k, v in self.error_dict.items():
                    error_dict.setdefault(k, []).extend(v)
            else:
                error_dict = self.error_dict
        else:
            error_dict['__all__'] = self.error_list
        return error_dict


class BaseSerializerField(object):

    error_messages = {
        'required': 'This field is required.',
        'invalid': 'Invalid value.',
    }
    validators = []
    default = None

    def __init__(self, required=True, mandatory=False, label=None, validators=[], error_messages=None, default=None):
        self.required = required
        self.mandatory = mandatory
        self.label = label
        self.data = None
        self._validators = self.validators + validators
        self._error_messages = {}
        for cls in reversed(self.__class__.__mro__):
            self._error_messages.update(getattr(cls, 'error_messages', {}))
        self._error_messages.update(error_messages or {})
        self.value = None


    def validate(self, value):
        if value in validators.VALIDATORS_EMPTY_VALUES and (self.required or self.mandatory):
            raise SerializerFieldValueError(self._error_messages['required'])
        errors = []
        for validator in self._validators:
            try:
                validator(value)
            except validators.SerializerValidatorError as e:
                if hasattr(e, 'error_code'):
                    message = self._error_messages[e.error_code]
                    errors.append(message)
                else:
                    errors.extend((e.message))
        if errors:
            raise SerializerFieldValueError(errors)
        self.value = value

    def set_value(self, value):
        self.validate(value=value)

    def _to_python(self):
        raise NotImplemented()

    def _to_native(self):
        raise NotImplemented()

    def to_native(self):
        try:
            result = self._to_native()
        except:
            raise SerializerFieldValueError(self._error_messages['invalid'])
        else:
            return result

    def to_python(self):
        try:
            result = self._to_python()
        except:
            raise SerializerFieldValueError(self._error_messages['invalid'])
        else:
            return result



class IntegerField(BaseSerializerField):
    validators = [validators.validate_integer,]

    def to_int(self, value):
        return int(value)

    def _to_native(self):
        return self.to_int(self.value)

    def _to_python(self):
        return self.to_int(self.value)


class FloatField(BaseSerializerField):
    validators = [validators.validate_float,]

    def to_float(self, value):
        return float(value)

    def _to_native(self):
        return self.to_float(self.value)

    def _to_python(self):
        return self.to_float(self.value)


class StringField(BaseSerializerField):
    validators = [validators.validate_string,]

    def to_unicode(self, value):
        return unicode(value)

    def _to_native(self):
        return self.to_unicode(self.value)

    def _to_python(self):
        return self.to_unicode(self.value)


class UUIDField(BaseSerializerField):
    validators = [validators.validate_uuid,]

    def _to_native(self):
        return str(self.value)

    def _to_python(self):
        if isinstance(self.value, uuid.UUID):
            return self.value
        self.value = uuid.UUID(str(self.value))
        return self.value


class DatetimeField(BaseSerializerField):
    pass


class NestedSerializerField(BaseSerializerField):

    def __init__(self, serializer):
        super(NestedSerializerField, self).__init__()
        self._serializer = serializer

    def validate(self, value):
        pass

    def to_native(self):
        return self._serializer.to_native()

    def to_python(self):
        return self._serializer.to_python()
