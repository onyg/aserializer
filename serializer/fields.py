# -*- coding: utf-8 -*-

import logging
import uuid
from datetime import datetime, date, time

#from validators import (SerializerValidatorError,
#                        VALIDATORS_EMPTY_VALUES,
#                        validate_integer,)
import validators
logger = logging.getLogger(__name__)



class SerializerFieldValueError(Exception):

    def __init__(self, message):
        if isinstance(message, basestring):
            self.error_message = message
        elif isinstance(message, dict):
            self.error_dict = message
        elif isinstance(message, list):
            self.error_list = message
        else:
            self.message = message

    @property
    def errors(self):
        if hasattr(self, 'error_message'):
            return self.error_message
        if hasattr(self, 'error_list'):
            messages = []
            for message in self.error_list:
                messages.append(str(message))
            return messages
        return self.message


    #@property
    #def message_dict(self):
    #    message_dict = {}
    #    for field, messages in self.error_dict.items():
    #        message_dict[field] = []
    #        for message in messages:
    #            if isinstance(message, SerializerFieldValueError):
    #                message_dict[field].extend(message.messages)
    #            else:
    #                message_dict[field].append(str(message))
    #    return message_dict


    def __repr__(self):
        return self.errors

    #@property
    #def messages(self):
    #    if hasattr(self, 'error_dict'):
    #        message_list = self.error_dict.values()
    #    else:
    #        message_list = self.error_list
    #
    #    messages = []
    #    for message in message_list:
    #        if isinstance(message, SerializerFieldValueError):
    #            params = message.params
    #            message = message.message
    #            if params:
    #                message %= params
    #        message = str(message)
    #        messages.append(message)
    #    if len(messages) > 0 and isinstance(messages[0], basestring):
    #        return str(messages[0])
    #    return messages
    #
    #def __str__(self):
    #    if hasattr(self, 'error_dict'):
    #        return repr(self.message_dict)
    #    return repr(self.messages)
    #
    #def __repr__(self):
    #    return 'SerializerFieldValueError {}'.format(str(self.messages))
    #
    #def update_error_dict(self, error_dict):
    #    if hasattr(self, 'error_dict'):
    #        if error_dict:
    #            for k, v in self.error_dict.items():
    #                error_dict.setdefault(k, []).extend(v)
    #        else:
    #            error_dict = self.error_dict
    #    else:
    #        error_dict['__all__'] = self.error_list
    #    return error_dict


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
                if hasattr(e, 'error_code') and e.error_code in self._error_messages:
                    message = self._error_messages[e.error_code]
                    errors.append(message)
                else:
                    errors.append(e.message)
                #raise SerializerFieldValueError(errors)
        if errors:
            raise SerializerFieldValueError(errors)
        self.set_value(value)

    def set_value(self, value):
        self.value = value

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


    def __init__(self, max_value=None, min_value=None, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)
        if max_value is not None:
            self._validators.append(validators.MaxValueValidator(max_value))
        if min_value is not None:
            self._validators.append(validators.MinValueValidator(min_value))

    def to_int(self, value):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        return int(value)

    def _to_native(self):
        return self.to_int(self.value)

    def _to_python(self):
        return self.to_int(self.value)


class FloatField(IntegerField):
    validators = [validators.validate_float,]

    def to_float(self, value):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        return float(value)

    def _to_native(self):
        return self.to_float(self.value)

    def _to_python(self):
        return self.to_float(self.value)


class StringField(BaseSerializerField):
    validators = [validators.validate_string,]

    def to_unicode(self, value):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return u''
        return unicode(value)

    def _to_native(self):
        return self.to_unicode(self.value)

    def _to_python(self):
        return self.to_unicode(self.value)


class UUIDField(BaseSerializerField):
    validators = [validators.validate_uuid,]

    def _to_native(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return ''
        return str(self.value)

    def _to_python(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, uuid.UUID):
            return self.value
        self.value = uuid.UUID(str(self.value))
        return self.value


class BaseDatetimeField(BaseSerializerField):
    date_formats = ['%Y-%m-%dT%H:%M:%S',]

    def __init__(self, formats=None, *args, **kwargs):
        super(BaseDatetimeField, self).__init__(*args, **kwargs)
        self._date_formats = formats or self.date_formats
        #self.strftime_format = None


    def validate(self, value):
        if value in validators.VALIDATORS_EMPTY_VALUES and (self.required or self.mandatory):
            raise SerializerFieldValueError(self._error_messages['required'])
        if self._is_instance(value):
            self.value = value
            return

        value = self.strptime(value, self._date_formats)
        self.set_value(value)

    def set_value(self, value):
        if self._is_instance(value):
            self.value = value
        else:
            raise SerializerFieldValueError(self._error_messages['invalid'])

    def _is_instance(self, value):
        return False

    def strptime(self, value, formats):
        for f in formats:
            try:
                result = datetime.strptime(value, f)
            except (ValueError, TypeError):
                continue
            else:
                return result
        return None


class DatetimeField(BaseDatetimeField):

    date_formats = ['%Y-%m-%dT%H:%M:%S',]

    def _is_instance(self, value):
        return isinstance(value, datetime)

    def _to_native(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, datetime):
            return self.value.isoformat()
        return str(self.value)

    def _to_python(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, datetime):
            return self.value
        self.value = self.strptime(self.value, self._date_formats)
        return self.value


class DateField(BaseDatetimeField):

    date_formats = ['%Y-%m-%d',]

    def _is_instance(self, value):
        return isinstance(value, date)

    def set_value(self, value):
        if isinstance(value, datetime):
            self.value = value.date()
        else:
            super(DateField, self).set_value(value)

    def _to_native(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, date):
            return self.value.isoformat()
        return str(self.value)

    def _to_python(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, date):
            return self.value
        _value = self.strptime(self.value, self._date_formats)
        if _value:
            self.value = _value.date()
        return self.value


class TimeField(BaseDatetimeField):

    date_formats = ['%H:%M:%S',]

    def _is_instance(self, value):
        return isinstance(value, time)

    def set_value(self, value):
        if isinstance(value, datetime):
            self.value = value.time()
        else:
            super(TimeField, self).set_value(value)

    def _to_native(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, time):
            return self.value.isoformat()
        return str(self.value)

    def _to_python(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, time):
            return self.value
        _value = self.strptime(self.value, self._date_formats)
        if _value:
            self.value = _value.time()
        return self.value


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
