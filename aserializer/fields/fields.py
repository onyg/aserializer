# -*- coding: utf-8 -*-

import uuid
import decimal

from collections import Iterable

from aserializer.utils import py2to3
from aserializer.fields.base import BaseSerializerField, IgnoreField, SerializerFieldValueError
from aserializer.fields import validators as v


class TypeField(BaseSerializerField):

    def __init__(self, name, fixed=False, validate=False,  *args, **kwargs):
        super(TypeField, self).__init__(*args, **kwargs)
        self.name = name
        self._initial_name = name
        self.identity = True
        self.error_messages = {}
        self.should_validate = validate
        self.fixed = fixed

    def validate(self):
        if self.should_validate:
            if self.name != self._initial_name:
                raise SerializerFieldValueError('Value is not {}.'.format(self._initial_name), field_names=self.names)

    def set_value(self, value):
        if not self.fixed:
            self.name = value

    def to_native(self):
        return py2to3._unicode(self.name)

    def to_python(self):
        return py2to3._unicode(self.name)

    def __set__(self, instance, value):
        pass


class IntegerField(BaseSerializerField):

    validators = [v.validate_integer, ]

    def __init__(self, max_value=None, min_value=None, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)
        if max_value is not None:
            self._validators.append(v.MaxValueValidator(max_value))
        if min_value is not None:
            self._validators.append(v.MinValueValidator(min_value))

    @staticmethod
    def to_int(value):
        if value in v.VALIDATORS_EMPTY_VALUES:
            return None
        return int(value)

    def _to_native(self):
        return self.to_int(self.value)

    def _to_python(self):
        return self.to_int(self.value)


class FloatField(IntegerField):
    validators = [v.validate_float, ]

    @staticmethod
    def to_float(value):
        if value in v.VALIDATORS_EMPTY_VALUES:
            return None
        return float(value)

    def _to_native(self):
        return self.to_float(self.value)

    def _to_python(self):
        return self.to_float(self.value)


class DecimalField(IntegerField):
    OUTPUT_AS_FLOAT = 0
    OUTPUT_AS_STRING = 1
    validators = [v.validate_decimal, ]

    def __init__(self, decimal_places=3, precision=None, max_value=None, min_value=None, output=None, **kwargs):
        super(DecimalField, self).__init__(max_value=max_value, min_value=min_value, **kwargs)
        self.decimal_places = decimal_places
        self.precision = precision
        if self.value and not isinstance(self.value, decimal.Decimal):
            self.set_value(self.value)
        if output is None or output not in (0, 1):
            self.output = self.OUTPUT_AS_FLOAT
        else:
            self.output = output

    def set_value(self, value):
        context = decimal.getcontext().copy()
        if self.precision is not None:
            context.prec = self.precision
        if isinstance(value, decimal.Decimal):
            self.value = value.quantize(decimal.Decimal(".1") ** self.decimal_places, context=context)
        elif isinstance(value, (py2to3.integer, float,)):
            self.value = decimal.Decimal(value).quantize(decimal.Decimal(".1") ** self.decimal_places, context=context)
        elif isinstance(value, py2to3.string):
            try:
                self.value = decimal.Decimal(value).quantize(decimal.Decimal(".1") ** self.decimal_places, context=context)
            except:
                self.value = value
        else:
            self.value = None

    def _to_native(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        if self.output == self.OUTPUT_AS_STRING:
            result = str(self.value)
        else:
            result = float(u'{}'.format(self.value))
        return result

    def _to_python(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        return self.value

    @staticmethod
    def __pre_eq__(other):
        if isinstance(other, decimal.Decimal):
            return other
        elif isinstance(other, py2to3.integer):
            return decimal.Decimal(other)
        elif isinstance(other, float):
            return decimal.Decimal(str(other))
        elif isinstance(other, py2to3.string):
            try:
                d = decimal.Decimal(str(other))
            except:
                raise ValueError()
            else:
                return d
        raise ValueError()

    def __eq__(self, other):
        if not isinstance(self.value, decimal.Decimal):
            return False
        try:
            _other = self.__pre_eq__(other=other)
        except ValueError:
            return False
        else:
            return self.value == _other


class BooleanField(BaseSerializerField):

    def __init__(self, required=False, *args, **kwargs):
        super(BooleanField, self).__init__(required=required, *args, **kwargs)

    def set_value(self, value):
        if value in v.VALIDATORS_EMPTY_VALUES:
            self.value = None
        elif isinstance(value, py2to3.string) and value.lower() in ('false', '0'):
            self.value = False
        else:
            self.value = bool(value)

    def _to_native(self):
        return self.value

    def _to_python(self):
        return self.value

    def to_native(self):
        result = super(BooleanField, self).to_native()
        return bool(result)


class StringField(BaseSerializerField):
    validators = [v.validate_string, ]

    def __init__(self, max_length=None, min_length=None, **kwargs):
        super(StringField, self).__init__( **kwargs)
        if max_length is not None:
            self._validators.append(v.MaxStringLengthValidator(max_length))
        if min_length is not None:
            self._validators.append(v.MinStringLengthValidator(min_length))

    @staticmethod
    def to_unicode(value):
        if value in v.VALIDATORS_EMPTY_VALUES:
            return u''
        return py2to3._unicode(value)

    def _to_native(self):
        return self.to_unicode(self.value)

    def _to_python(self):
        return self.to_unicode(self.value)


class EmailField(StringField):
    validators = [v.validate_email, ]


class UUIDField(BaseSerializerField):
    validators = [v.validate_uuid, ]

    def __init__(self, upper=True, binary=True, *args, **kwargs):
        """
        To native always returns a string representation.  Upper specifies if it should be upper- or lower-case
        To python returns a UUID object if binary is True (default), otherwise a lowercase string uuid.
        """
        super(UUIDField, self).__init__(*args, **kwargs)
        self.upper = upper
        self.binary = binary

    def _to_native(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return u''
        if self.upper:
            return py2to3._unicode(self.value).upper()
        else:
            return py2to3._unicode(self.value)

    def _to_python(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        if self.binary and not isinstance(self.value, uuid.UUID):
            self.value = uuid.UUID(str(self.value))
        if not self.binary:
            return py2to3._unicode(self.value).lower()
        return self.value


class UrlField(BaseSerializerField):

    validators = [v.validate_url, ]

    def __init__(self, base=None, *args, **kwargs):
        super(UrlField, self).__init__(*args, **kwargs)
        self.uri_base = base
        if self.uri_base and not str(self.uri_base).endswith('/'):
            self.uri_base = '{}/'.format(self.uri_base)
        if self.value:
            self.set_value(value=self.value)

    @staticmethod
    def to_unicode(value):
        if value in v.VALIDATORS_EMPTY_VALUES:
            return u''
        return py2to3._unicode(value)

    def set_value(self, value):
        if self.uri_base:
            self.value = '{}{}'.format(self.uri_base, value)
        else:
            self.value = value

    def _to_native(self):
        return self.to_unicode(self.value)

    def _to_python(self):
        return self.to_unicode(self.value)


class ChoiceField(BaseSerializerField):

    error_messages = {
        'required': 'This field is required.',
        'invalid': 'Invalid choice value.',
    }

    def __init__(self, choices=None, upper=False, *args, **kwargs):
        super(ChoiceField, self).__init__(*args, **kwargs)
        self.choices = choices or ()
        self.upper = upper
        self.set_value(self.value)

    def set_value(self, value):
        if self.upper and isinstance(value, py2to3.string):
            value = value.lower()
        self.value = value
        self.python_value = self._get_value(value, to_python=True)
        self.native_value = self._get_value(value, to_python=False)

    def _get_key_value_from_choice_element(self, choice):
        if isinstance(choice, (list, tuple,)):
            try:
                val = choice[0]
                key = choice[1]
            except IndexError:
                return None, None
            return key, val
        return choice, choice

    def _get_value(self, value, to_python=True):
        if value in v.VALIDATORS_EMPTY_VALUES:
            return None
        for choice in self.choices:
            key, val = self._get_key_value_from_choice_element(choice)
            if value == key or value == val:
                if to_python:
                    return val
                else:
                    return key
        return None

    def validate(self):
        super(ChoiceField, self).validate()
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return
        _val = self._get_value(self.value)
        if _val is None:
            raise SerializerFieldValueError(self._error_messages['invalid'], field_names=self.names)

    def _to_native(self):
        value = self.native_value
        if self.upper and isinstance(value, py2to3.string):
            value = value.upper()
        return value

    def _to_python(self):
        value = self.python_value
        if self.upper and isinstance(value, py2to3.string):
            value = value.lower()
        return value

class ListField(BaseSerializerField):

    def __init__(self, field, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)
        self._field_cls = field
        self.items = []
        self._python_items = []
        self._native_items = []

    def validate(self):
        if self.items:
            _errors = []
            for field in self.items:
                try:
                    field.validate()
                except SerializerFieldValueError as e:
                    _errors.append(e.errors)
            if _errors:
                raise SerializerFieldValueError(_errors)
        elif self.required:
            raise SerializerFieldValueError(self._error_messages['required'], field_names=self.names)

    def add_item(self, value):
        field = self._field_cls()
        field.set_value(value=value)
        self.items.append(field)

    def set_value(self, value):
        self.items[:] = []
        self._native_items[:] = []
        self._python_items[:] = []
        if isinstance(value, Iterable):
            for item in value:
                self.add_item(value=item)

    def _to_native(self):
        if not self._native_items:
            for field in self.items:
                self._native_items.append(field.to_native())
        return self._native_items

    def _to_python(self):
        if not self._python_items:
            for field in self.items:
                self._python_items.append(field.to_python())
        return self._python_items


    def append(self, value):
        self.add_item(value=value)
        self.validate()

    def __iter__(self):
        return self.to_python().__iter__()

    def __get__(self, instance, owner):
        if instance is None:
            return self
        field, field_name = self._get_field_from_instance(instance=instance)
        return field

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

    def __setitem__(self, i, value):
        del self.items[i]
        self.add_item(value=value)
        self.validate()

    def __getitem__(self, y):
        return self.to_python()[y]

    def __len__(self):
        return len(self.items)

    def __contains__(self, value):
        return value in self.to_python()
