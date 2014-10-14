===========
aserializer
===========

About
=====

aserializer is an object serializer inspired by the django forms.


Examples
========
**Examples how code looks like**::

  class Address(Serializer):
      id = IntegerField(required=True, identity=True)
      street = StringField(required=True)
      streetNumber = StringField(required=True)
      city = StringField(required=False)
      country = StringField(required=False)

  class User(Serializer):
      _type = TypeField('user')
      id = IntegerField(required=True, identity=True)
      name = StringField(required=True)
      email = EmailField(required=True)
      tel = StringField(required=False, min_length=10, max_length=50)
      address = SerializerField(Address, required=True)


**Result**::

  user = User(DATA)
  user.dump()

  {
    "_type": "user",
    "id": 1,
    "name": "Joe",
    "email": "joe@example.com",
    "tel": "+49 555 555 12",
    "address": {
      "id": 1,
      "street": "Street",
      "streetNumber": "5a",
      "city": "Berlin",
      "country": "Germany"
    }
  }


Tests
=====
To run the tests use the command: ``python setup.py nosetests``


Contributing
============

Please find bugs and send pull requests to the `GitHub repository`_ and `issue tracker`_.

.. _GitHub repository: https://github.com/onyg/aserializer
.. _issue tracker: https://github.com/onyg/aserializer/issues