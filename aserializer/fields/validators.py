# -*- coding: utf-8 -*-
import uuid
import re
import decimal

from aserializer.utils import py2to3

VALIDATORS_EMPTY_VALUES = (None, 'null', '', u'', [], (), {})


class SerializerValidatorError(Exception):
    error_code = None
    message = ''

    def __init__(self, message=None, error_code=None, params=None):
        self.message = message or self.message
        self.error_code = error_code or self.error_code
        if params:
            self.message %= params

    def __str__(self):
        return repr(self.message)

    def __repr__(self):
        return u'{}'.format(self.message)



class SerializerInvalidError(SerializerValidatorError):
    error_code = 'invaid'


class SerializerRequiredError(SerializerValidatorError):
    error_code = 'required'


class CompareValidator(object):
    compare = lambda self, a, b: a is not b
    message = 'Value should be %(compare_value)s (it is %(value)s).'
    error_code = 'compare'

    def __init__(self, compare_value):
        self.compare_value = compare_value

    def __call__(self, value):
        if self.compare(value, self.compare_value):
            self.raise_validation_error(value)

    def raise_validation_error(self, value):
        params = {'compare_value': self.compare_value, 'value': value}
        raise SerializerValidatorError(message=self.message, error_code=self.error_code, params=params)


class ConvertAndCompareValidator(CompareValidator):
    """
    Some fields might require casting of string values to the type of the compare_value.

    """
    def __call__(self, value):
        if isinstance(value, py2to3.string) and not isinstance(self.compare_value, py2to3.string):
            try:
                value = type(self.compare_value)(value)
            except ValueError:
                return

        super(ConvertAndCompareValidator, self).__call__(value)


class MaxValueValidator(ConvertAndCompareValidator):
    compare = lambda self, a, b: a > b
    message = 'Value is greater than %(compare_value)s.'
    error_code = 'max_value'


class MinValueValidator(ConvertAndCompareValidator):
    compare = lambda self, a, b: a < b
    message = 'Value is less than %(compare_value)s.'
    error_code = 'min_value'


def validate_integer(value):
    try:
        int(value)
    except (ValueError, TypeError):
        raise SerializerValidatorError('Enter a valid integer.', error_code='invalid')


def validate_float(value):
    try:
        float(value)
    except (ValueError, TypeError):
        raise SerializerValidatorError('Enter a valid float.', error_code='invalid')

def validate_decimal(value):
    if isinstance(value, decimal.Decimal):
        return
    try:
        decimal.Decimal(value)
    except (ValueError, TypeError, decimal.InvalidOperation,):
        raise SerializerValidatorError('Enter a valid decimal.', error_code='invalid')


def validate_string(value):
    if not isinstance(value, py2to3.string):
        raise SerializerValidatorError('Enter a valid string.', error_code='invalid')


class MinStringLengthValidator(CompareValidator):
    compare = lambda self, a, b: len(py2to3._unicode(a)) < b
    message = 'Value is too short. Minimum value length is %(compare_value)s.'
    code = 'min_length'


class MaxStringLengthValidator(CompareValidator):
    compare = lambda self, a, b: len(py2to3._unicode(a)) > b
    message = 'Value is too long. Maximum value length is %(compare_value)s.'
    code = 'max_length'


RE_UUID = re.compile(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', re.I)

def validate_uuid(value):
    if not isinstance(value, uuid.UUID):
       if not RE_UUID.search(py2to3._unicode(value)):
            raise SerializerValidatorError('Enter a valid uuid.', error_code='invalid')


RE_URL = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def validate_url(value):
   if not RE_URL.search(py2to3._unicode(value)):
        raise SerializerValidatorError('Enter a valid url.', error_code='invalid')


RE_EMAIL= re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)

def validate_email(value):
   if not RE_EMAIL.search(py2to3._unicode(value)):
        raise SerializerValidatorError('Enter a valid email.', error_code='invalid')
