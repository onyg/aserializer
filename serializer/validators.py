# -*- coding: utf-8 -*-
import uuid
import re

VALIDATORS_EMPTY_VALUES = (None, '', [], (), {})


#class SerializerValidatorError(Exception):
#    error_code = None
#
#    def __init__(self, message, error_code=None):
#        if isinstance(message, dict):
#            self.error_dict = message
#        elif isinstance(message, list):
#            self.error_list = message
#        else:
#            self.message = message
#
#        if error_code is not None:
#            self.error_code = error_code
#
#    @property
#    def message_dict(self):
#        message_dict = {}
#        for field, messages in self.error_dict.items():
#            message_dict[field] = []
#            for message in messages:
#                if isinstance(message, SerializerValidatorError):
#                    message_dict[field].extend(message.messages)
#                else:
#                    message_dict[field].append(str(message))
#        return message_dict
#
#    @property
#    def messages(self):
#        if hasattr(self, 'error_dict'):
#            message_list = self.error_dict.values()
#        else:
#            message_list = self.error_list
#
#        messages = []
#        for message in message_list:
#            if isinstance(message, SerializerValidatorError):
#                params = message.params
#                message = message.message
#                if params:
#                    message %= params
#            message = str(message)
#            messages.append(message)
#        return messages
#
#    def __str__(self):
#        if hasattr(self, 'error_dict'):
#            return repr(self.message_dict)
#        return repr(self.messages)
#
#    def __repr__(self):
#        return 'SerializerValidatorError{}'.format(self)
#
#    def update_error_dict(self, error_dict):
#        if hasattr(self, 'error_dict'):
#            if error_dict:
#                for k, v in self.error_dict.items():
#                    error_dict.setdefault(k, []).extend(v)
#            else:
#                error_dict = self.error_dict
#        else:
#            error_dict['__all__'] = self.error_list
#        return error_dict


class SerializerValidatorError(Exception):
    error_code = None
    message = ''

    def __init__(self, message=None, error_code=None):
        self.message = message or self.message
        self.error_code = error_code or self.error_code

    def __str__(self):
        return repr(self.message)

    def __repr__(self):
        return u'{}'.format(self.message)



class SerializerInvalidError(SerializerValidatorError):
    error_code = 'invaid'


class SerializerRequiredError(SerializerValidatorError):
    error_code = 'required'


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


def validate_string(value):
    if not isinstance(value, basestring):
        raise SerializerValidatorError('Enter a valid string.', error_code='invalid')


RE_UUID = re.compile(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', re.I)

def validate_uuid(value):
    if not isinstance(value, uuid.UUID):
       if not RE_UUID.search(unicode(value)):
            raise SerializerValidatorError('Enter a valid uuid.', error_code='invalid')