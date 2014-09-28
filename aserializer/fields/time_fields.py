# -*- coding: utf-8 -*-

from datetime import datetime, date, time

from aserializer.utils import py2to3
from aserializer.fields.base import BaseSerializerField, SerializerFieldValueError
from aserializer.fields import validators as v


class BaseDatetimeField(BaseSerializerField):
    date_formats = ['%Y-%m-%dT%H:%M:%S.%f', ]
    error_messages = {
        'required': 'This field is required.',
        'invalid': 'Invalid date value.',
    }

    def __init__(self, formats=None, serialize_to=None, *args, **kwargs):
        super(BaseDatetimeField, self).__init__(*args, **kwargs)
        self._date_formats = formats or self.date_formats
        self._serialize_format = serialize_to
        self._current_format = None
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
        elif isinstance(value, py2to3.string):
            self.value = self.strptime(value, self._date_formats)
            self.invalid = self.value is None

    def _is_instance(self, value):
        return False

    def strptime(self, value, formats):
        for f in formats:
            try:
                result = datetime.strptime(value, f)
                self._current_format = f
            except (ValueError, TypeError):
                continue
            else:
                return result
        return None

    def strftime(self, value):
        if self._serialize_format:
            return value.strftime(self._serialize_format)
        elif self._current_format:
            return value.strftime(self._current_format)
        else:
            return py2to3._unicode(value.isoformat())


class DatetimeField(BaseDatetimeField):

    date_formats = ['%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S']
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
            return self.strftime(self.value)
        return py2to3._unicode(self.value)

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
        elif isinstance(value, py2to3.string):
            _value = self.strptime(value, self._date_formats)
            if _value is not None:
                self.value = _value.date()
            self.invalid = _value is None

    def _to_native(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, date):
            return self.strftime(self.value)
        return py2to3._unicode(self.value)

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
        elif isinstance(value, py2to3.string):
            _value = self.strptime(value, self._date_formats)
            if _value is not None:
                self.value = _value.time()
            self.invalid = _value is None

    def _to_native(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, time):
            return self.strftime(self.value)
        return py2to3._unicode(self.value)

    def _to_python(self):
        if self.value in v.VALIDATORS_EMPTY_VALUES:
            return None
        if isinstance(self.value, time):
            return self.value
        _value = self.strptime(self.value, self._date_formats)
        if _value:
            self.value = _value.time()
        return self.value
