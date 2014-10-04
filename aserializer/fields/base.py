# -*- coding: utf-8 -*-

from aserializer.utils import py2to3
from aserializer.fields import validators as v


class IgnoreField(Exception):
    pass


class SerializerFieldValueError(Exception):

    def __init__(self, message, field_names=None):
        if isinstance(message, py2to3.string):
            self.error_message = message
        elif isinstance(message, dict):
            self.error_dict = message
        elif isinstance(message, list):
            self.error_list = message
        self.message = str(message)
        if field_names:
            self.field_name = ','.join(field_names)
        else:
            self.field_name = 'field'

    @property
    def errors(self):
        if hasattr(self, 'error_message'):
            return self.error_message
        if hasattr(self, 'error_list'):
            return self.error_list
        if hasattr(self, 'error_dict'):
            return self.error_dict
        return self.message

    def __repr__(self):
        return self.errors

    def __str__(self):
        return '[{}]: {}'.format(self.field_name, self.message)


HIDE_FIELD = 0


class BaseSerializerField(object):

    error_messages = {
        'required': 'This field is required.',
        'invalid': 'Invalid value.',
        'identity_missing': 'Identity is missing'
    }
    validators = []

    def __init__(self, required=True, identity=False,
                 label=None, map_field=None, on_null=None,
                 action_field=False, error_messages=None, default=None, validators=None):
        self.required = required
        self.identity = identity
        self.label = label
        self.map_field = map_field
        self._validators = []
        self._validators.extend(self.validators)
        if isinstance(validators, (list, tuple,)):
            self._validators.extend(validators)
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
        self.ignore = False

    def add_name(self, name):
        self.names = list(set(self.names + [name]))

    def validate(self):
        if self.ignore:
            return
        is_empty_value = self.value in v.VALIDATORS_EMPTY_VALUES
        if is_empty_value and (self.required or self.identity):
            raise SerializerFieldValueError(self._error_messages['required'])
        elif is_empty_value and not (self.required or self.identity):
            return

        errors = []
        for validator in self._validators:
            try:
                validator(self.value)
            except v.SerializerValidatorError as e:
                if hasattr(e, 'error_code') and e.error_code in self._error_messages:
                    message = self._error_messages[e.error_code]
                    errors.append(message)
                else:
                    errors.append(e.message)
        if errors:
            raise SerializerFieldValueError(' '.join(errors), field_names=self.names)

    def set_value(self, value):
        self.value = value

    def _to_python(self):
        raise NotImplemented()

    def _to_native(self):
        raise NotImplemented()

    def to_native(self):
        if self.ignore:
            raise IgnoreField()
        try:
            result = self._to_native()
        except SerializerFieldValueError:
            raise
        except:
            raise SerializerFieldValueError(self._error_messages['invalid'], field_names=self.names)
        else:
            if (self.identity and self.required) and result in v.VALIDATORS_EMPTY_VALUES:
                raise SerializerFieldValueError(self._error_messages['required'], field_names=self.names)
            elif result in v.VALIDATORS_EMPTY_VALUES and self.on_null_value == HIDE_FIELD:
                raise IgnoreField()
            return result

    def to_python(self):
        try:
            result = self._to_python()
        except SerializerFieldValueError:
            raise
        except:
            raise SerializerFieldValueError(self._error_messages['invalid'], field_names=self.names)
        else:
            if (self.identity and self.required) and result in v.VALIDATORS_EMPTY_VALUES:
                raise SerializerFieldValueError(self._error_messages['required'], field_names=self.names)
            elif result in v.VALIDATORS_EMPTY_VALUES and self.on_null_value == HIDE_FIELD:
                return None
            return result

    def _get_field_from_instance(self, instance):
        for name in self.names:
            if name in instance._data:
                return instance._data[name], name
        return None, None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        field, field_name = self._get_field_from_instance(instance=instance)
        if field:
            try:
                value = instance._field_to_python(field_name=field_name, field=field)
            except IgnoreField:
                return None
            else:
                return value
        return self

    def __set__(self, instance, value):
        if instance is None:
            return
        field, field_name = self._get_field_from_instance(instance=instance)
        if field is None:
            return
        self.ignore = False
        for name in self.names:
            try:
                value = instance.clean_field_value(name, value)
            except IgnoreField:
                self.ignore = True
        field.set_value(value=value)
        field.validate()
        instance.update_field(field)
