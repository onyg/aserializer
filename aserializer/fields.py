# -*- coding: utf-8 -*-

import logging
import uuid
import decimal
from datetime import datetime, date, time
from decimal import Decimal
from collections import Iterable
import validators as v

logger = logging.getLogger(__name__)


_serializer_registry = {}


class SerializerNotRegistered(Exception):
    message = 'Not in register.'


def register_serializer(name, cls):
    if name in _serializer_registry:
        return
    _serializer_registry[name] = cls


def get_serializer(name):
    if name in _serializer_registry:
        return _serializer_registry[name]
    raise SerializerNotRegistered()


class IgnoreField(Exception):
    pass


class SerializerFieldValueError(Exception):

    def __init__(self, message, field_names=None):
        if isinstance(message, basestring):
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
                    #break
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
        except SerializerFieldValueError, e:
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
        except SerializerFieldValueError, e:
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
                return instance._data[name]
        return None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        field = self._get_field_from_instance(instance=instance)
        if field:
            return field.to_python()
        return self

    def __set__(self, instance, value):
        if instance is None:
            return
        field = self._get_field_from_instance(instance=instance)
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


class TypeField(BaseSerializerField):

    def __init__(self, name, fixed=False, *args, **kwargs):
        super(TypeField, self).__init__(*args, **kwargs)
        self.name = name
        self.identity = True
        self.error_messages = {}
        self.fixed = fixed

    def validate(self):
        pass

    def set_value(self, value):
        if not self.fixed:
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
        elif isinstance(value, (int, long, float,)):
            self.value = decimal.Decimal(value).quantize(decimal.Decimal(".1") ** self.decimal_places, context=context)
        elif isinstance(value, basestring):
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
        elif isinstance(other, (int, long)):
            return Decimal(other)
        elif isinstance(other, float):
            return Decimal(str(other))
        elif isinstance(other, basestring):
            try:
                d = Decimal(str(other))
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

    def set_value(self, value):
        if value in v.VALIDATORS_EMPTY_VALUES:
            self.value = None
        elif isinstance(value, basestring) and value.lower() in ('false', '0'):
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
        return unicode(value)

    def _to_native(self):
        return self.to_unicode(self.value)

    def _to_python(self):
        return self.to_unicode(self.value)


class EmailField(StringField):
    validators = [v.validate_email, ]


class UUIDField(BaseSerializerField):
    validators = [v.validate_uuid, ]

    def _to_native(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return u''
        return unicode(self.value)

    def _to_python(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, uuid.UUID):
            return self.value
        self.value = uuid.UUID(str(self.value))
        return self.value


class BaseDatetimeField(BaseSerializerField):
    date_formats = ['%Y-%m-%dT%H:%M:%S.%f', ]
    error_messages = {
        'required': 'This field is required.',
        'invalid': 'Invalid date value.',
    }

    def __init__(self, formats=None, *args, **kwargs):
        super(BaseDatetimeField, self).__init__(*args, **kwargs)
        self._date_formats = formats or self.date_formats
        self.invalid = False

    def validate(self):
        if self.ignore:
            return
        if self.invalid:
            raise SerializerFieldValueError(self._error_messages['invalid'], field_names=self.names)
        if self.value in v.VALIDATORS_EMPTY_VALUES and (self.required or self.identity):
            raise SerializerFieldValueError(self._error_messages['required'], field_names=self.names)
        if self._is_instance(self.value):
            return

        _value = self.strptime(self.value, self._date_formats)
        if _value is None and self.invalid:
            raise SerializerFieldValueError(self._error_messages['invalid'], field_names=self.names)

    def set_value(self, value):
        if self._is_instance(value):
            self.value = value
        elif isinstance(value, basestring):
            self.value = self.strptime(value, self._date_formats)
            self.invalid = self.value is None

    def _is_instance(self, value):
        return False

    @staticmethod
    def strptime(value, formats):
        for f in formats:
            try:
                result = datetime.strptime(value, f)
            except (ValueError, TypeError):
                continue
            else:
                return result
        return None


class DatetimeField(BaseDatetimeField):

    date_formats = ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S']
    error_messages = {
        'required': 'This field is required.',
        'invalid': 'Invalid date time value.',
    }

    def _is_instance(self, value):
        return isinstance(value, datetime)

    def _to_native(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, datetime):
            return unicode(self.value.isoformat())
        return unicode(self.value)

    def _to_python(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, datetime):
            return self.value
        self.value = self.strptime(self.value, self._date_formats)
        return self.value


class DateField(BaseDatetimeField):

    date_formats = ['%Y-%m-%d', ]
    error_messages = {
        'required': 'This field is required.',
        'invalid': 'Invalid date value.',
    }

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
            self.invalid = _value is None

    def _to_native(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, date):
            return unicode(self.value.isoformat())
        return unicode(self.value)

    def _to_python(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, date):
            return self.value
        _value = self.strptime(self.value, self._date_formats)
        if _value:
            self.value = _value.date()
        return self.value


class TimeField(BaseDatetimeField):

    date_formats = ['%H:%M:%S', ]
    error_messages = {
        'required': 'This field is required.',
        'invalid': 'Invalid time value.',
    }

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
            self.invalid = _value is None

    def _to_native(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, time):
            return unicode(self.value.isoformat())
        return unicode(self.value)

    def _to_python(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, time):
            return self.value
        _value = self.strptime(self.value, self._date_formats)
        if _value:
            self.value = _value.time()
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


class ChoiceField(BaseSerializerField):

    error_messages = {
        'required': 'This field is required.',
        'invalid': 'Invalid choice value.',
    }

    def __init__(self, choices=(), *args, **kwargs):
        super(ChoiceField, self).__init__(*args, **kwargs)
        self.choices = choices
        self.python_value = None

    def validate(self):
        super(ChoiceField, self).validate()
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return
        for val in self.choices:
            if isinstance(val, (list, tuple)):
                try:
                    val2 = val[0]
                    key2 = val[1]
                except:
                    continue
                else:
                    if self.value == key2:
                        self.python_value = val2
                        return
            else:
                if self.value == val:
                    self.python_value = val
                    return
        raise SerializerFieldValueError(self._error_messages['invalid'], field_names=self.names)

    def _to_native(self):
        return self.value

    def _to_python(self):
        return self.python_value


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
                except SerializerFieldValueError, e:
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
        field = self._get_field_from_instance(instance=instance)
        return field

    def __set__(self, instance, value):
        if instance is None:
            return
        field = self._get_field_from_instance(instance=instance)
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


class SerializerObjectField(BaseSerializerField):

    def __init__(self, *args, **kwargs):
        super(SerializerObjectField, self).__init__(*args, **kwargs)
        self.only_fields = []
        self.exclude = []
        self.extras = {}
        self._serializer_cls = None

    @staticmethod
    def normalize_serializer_cls(serializer_cls):
        if isinstance(serializer_cls, basestring):
            serializer_cls = get_serializer(serializer_cls)
        return serializer_cls

    def get_serializer_cls(self):
        return self.normalize_serializer_cls(self._serializer_cls)

    def pre_value(self, fields=None, exclude=None, **extras):
        self.only_fields = fields
        self.exclude = exclude
        self.extras = extras

    def get_instance(self):
        return None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        field = self._get_field_from_instance(instance=instance)
        if field:
            return field.get_instance()
        return self


class NestedSerializerField(SerializerObjectField):

    def __init__(self, serializer, *args, **kwargs):
        super(NestedSerializerField, self).__init__(*args, **kwargs)
        self._serializer_cls = serializer
        self._serializer = None

    def get_instance(self):
        return self._serializer

    def validate(self):
        if self._serializer:
            if not self._serializer.is_valid():
                raise SerializerFieldValueError(self._serializer.errors, field_names=self.names)
        elif self.required:
            raise SerializerFieldValueError(self._error_messages['required'], field_names=self.names)

    def set_value(self, value):
        if self._serializer is None:
            self._serializer_cls = self.normalize_serializer_cls(self._serializer_cls)
            self._serializer = self._serializer_cls(source=value,
                                                    fields=self.only_fields,
                                                    exclude=self.exclude,
                                                    **self.extras)
        else:
            self._serializer.initial(source=value)

    def _to_native(self):
        if self._serializer:
            return self._serializer.dump()
        return None

    def _to_python(self):
        if self._serializer:
            return self._serializer.to_dict()
        return None


class ListSerializerField(SerializerObjectField):

    error_messages = {
        'required': 'This list is empty.',
    }

    def __init__(self, serializer, *args, **kwargs):
        super(ListSerializerField, self).__init__(*args, **kwargs)
        self._serializer_cls = serializer
        self.items = []
        self.only_fields = []
        self.exclude = []
        self.extras = {}
        self._python_items = []
        self._native_items = []

    def validate(self):
        if self.items:
            _errors = []
            for item in self.items:
                if not item.is_valid():
                    _errors.append(item.errors)
            if _errors:
                raise SerializerFieldValueError(_errors)
        elif self.required:
            raise SerializerFieldValueError(self._error_messages['required'], field_names=self.names)

    def pre_value(self, fields=None, exclude=None, **extras):
        self.only_fields = fields
        self.exclude = exclude
        self.extras = extras

    def get_instance(self):
        return self.items

    def add_item(self, source):
        self._serializer_cls = self.normalize_serializer_cls(self._serializer_cls)
        _serializer = self._serializer_cls(source=source,
                                           fields=self.only_fields,
                                           exclude=self.exclude,
                                           **self.extras)
        self.items.append(_serializer)

    def set_value(self, value):
        self.items[:] = []
        self._native_items[:] = []
        self._python_items[:] = []
        if isinstance(value, Iterable):
            for item in value:
                self.add_item(source=item)

    def _to_native(self):
        if not self._native_items:
            for item in self.items:
                self._native_items.append(item.dump())
        return self._native_items

    def _to_python(self):
        if not self._python_items:
            for item in self.items:
                self._python_items.append(item.to_dict())
        return self._python_items
