# -*- coding: utf-8 -*-

import logging
import uuid
from datetime import datetime, date, time

#from validators import (SerializerValidatorError,
#                        VALIDATORS_EMPTY_VALUES,
#                        validate_integer,)
import validators
logger = logging.getLogger(__name__)


class IgnoreField(Exception):
    pass

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


    def __repr__(self):
        return self.errors


HIDE_FIELD = 0


class BaseSerializerField(object):

    error_messages = {
        'required': 'This field is required.',
        'invalid': 'Invalid value.',
    }
    validators = []
    default = None

    def __init__(self, required=True, identity=False, label=None, map_field=None, on_null=None, action_field=False, validators=[], error_messages=None, default=None):
        self.required = required
        self.identity = identity
        self.label = label
        self.map_field = map_field
        self.data = None
        self._validators = self.validators + validators
        self._error_messages = {}
        for cls in reversed(self.__class__.__mro__):
            self._error_messages.update(getattr(cls, 'error_messages', {}))
        self._error_messages.update(error_messages or {})
        self.value = default
        if default:
            self.has_default = True
        else:
            self.has_default = False
        self.names = []
        self.on_null_value = on_null
        self.action_field = action_field

    def add_name(self, name):
        self.names = list(set(self.names + [name]))


    def validate(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES and (self.required or self.identity):
            raise SerializerFieldValueError(self._error_messages['required'])
        if self.value is None and not (self.required or self.identity):
            return

        errors = []
        for validator in self._validators:
            try:
                validator(self.value)
            except validators.SerializerValidatorError as e:
                if hasattr(e, 'error_code') and e.error_code in self._error_messages:
                    message = self._error_messages[e.error_code]
                    errors.append(message)
                else:
                    errors.append(e.message)
        if errors:
            raise SerializerFieldValueError(errors)

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
            if (self.identity and self.required) and result in validators.VALIDATORS_EMPTY_VALUES:
                raise SerializerFieldValueError(self._error_messages['required'])
            elif result in validators.VALIDATORS_EMPTY_VALUES and self.on_null_value == HIDE_FIELD:
                raise IgnoreField()
            return result

    def to_python(self):
        try:
            result = self._to_python()
        except:
            raise SerializerFieldValueError(self._error_messages['invalid'])
        else:
            if (self.identity and self.required) and result in validators.VALIDATORS_EMPTY_VALUES:
                raise SerializerFieldValueError(self._error_messages['required'])
            elif result in validators.VALIDATORS_EMPTY_VALUES and self.on_null_value == HIDE_FIELD:
                return None
            return result

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.to_python()

    def __set__(self, instance, value):
        if instance is not None:
            for name in self.names:
                try:
                    value = instance.clean_field_value(name, value)
                except IgnoreField:
                    pass
        self.set_value(value=value)
        self.validate()
        if instance:
            instance.update_field(self)


class TypeField(BaseSerializerField):

    def __init__(self, name, *args, **kwargs):
        super(TypeField, self).__init__(*args, **kwargs)
        self.name = name
        self.identity = True
        self.error_messages = {}

    def validate(self):
        pass

    def set_value(self, value):
        self.name = value

    def to_native(self):
        return unicode(self.name)

    def to_python(self):
        return unicode(self.name)

    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        pass

class IntegerField(BaseSerializerField):
    validators = [validators.validate_integer,]

    def __init__(self, max_value=None, min_value=None, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)
        if max_value is not None:
            self._validators.append(validators.MaxValueValidator(max_value))
        if min_value is not None:
            self._validators.append(validators.MinValueValidator(min_value))

    def to_int(self, value):
        if value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        return int(value)

    def _to_native(self):
        return self.to_int(self.value)

    def _to_python(self):
        return self.to_int(self.value)


class FloatField(IntegerField):
    validators = [validators.validate_float,]

    def to_float(self, value):
        if value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        return float(value)

    def _to_native(self):
        return self.to_float(self.value)

    def _to_python(self):
        return self.to_float(self.value)


class StringField(BaseSerializerField):
    validators = [validators.validate_string,]

    def to_unicode(self, value):
        if value in validators.VALIDATORS_EMPTY_VALUES:
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
            return u''
        return unicode(self.value)

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


    def validate(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES and (self.required or self.mandatory):
            raise SerializerFieldValueError(self._error_messages['required'])
        if self._is_instance(self.value):
            return

        _value = self.strptime(self.value, self._date_formats)
        if _value is None and (self.required or self.mandatory):
            raise SerializerFieldValueError(self._error_messages['invalid'])

    def set_value(self, value):
        if self._is_instance(value):
            self.value = value
        elif isinstance(value, basestring):
            self.value = self.strptime(value, self._date_formats)

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
            return unicode(self.value.isoformat())
        return unicode(self.value)

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
        if self._is_instance(value):
            self.value = value
        elif isinstance(value, datetime):
            self.value = value.date()
        elif isinstance(value, basestring):
            _value = self.strptime(value, self._date_formats)
            if _value is not None:
                self.value = _value.date()

    def _to_native(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, date):
            return unicode(self.value.isoformat())
        return unicode(self.value)

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
        if self._is_instance(value):
            self.value = value
        elif isinstance(value, datetime):
            self.value = value.time()
        elif isinstance(value, basestring):
            _value = self.strptime(value, self._date_formats)
            if _value is not None:
                self.value = _value.time()

    def _to_native(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, time):
            return unicode(self.value.isoformat())
        return unicode(self.value)

    def _to_python(self):
        if self.value in validators.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, time):
            return self.value
        _value = self.strptime(self.value, self._date_formats)
        if _value:
            self.value = _value.time()
        return self.value


class UrlSerializerField(BaseSerializerField):

    validators = [validators.validate_url,]

    def __init__(self, base=None, *args, **kwargs):
        super(UrlSerializerField, self).__init__(*args, **kwargs)
        self.uri_base = base
        if self.uri_base and not str(self.uri_base).endswith('/'):
            self.uri_base = '{}/'.format(self.uri_base)
        if self.value:
            self.set_value(value=self.value)

    def to_unicode(self, value):
        if value in validators.VALIDATORS_EMPTY_VALUES:
            return u''
        return unicode(value)

    def set_value(self, value):
        if self.uri_base:
            self.value = '{}{}'.format(self.uri_base, value)
        else:
            self.value = value

    def _to_native(self):
        return self.to_unicode(self.value)

    def _to_python(self):
        return self.to_unicode(self.value)


class SerializerObjectField(BaseSerializerField):

    def __init__(self, *args, **kwargs):
        super(SerializerObjectField, self).__init__(*args, **kwargs)
        self.only_fields = []
        self.exlude = []

    def pre_value(self, fields=None, exclude=None):
        self.only_fields = fields
        self.exlude = fields


class NestedSerializerField(SerializerObjectField):

    def __init__(self, serializer_cls, *args, **kwargs):
        super(NestedSerializerField, self).__init__(*args, **kwargs)
        self._serializer_cls = serializer_cls

    def validate(self):
        pass

    def set_value(self, value):
        if self._serializer is None:
            self._serializer = self._serializer_cls(source=value,
                                                    fields=self.only_fields,
                                                    exclude=self.exlude)

    def to_native(self):
        return self._serializer.to_native()

    def to_python(self):
        return self._serializer.to_python()
