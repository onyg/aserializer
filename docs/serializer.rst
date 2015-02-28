===========
Serializers
===========

Serializers are the core objects of ``aserializer``. They do the main work of converting data into
native Python datatypes and into easily rendered data values. Serializers providing parsing of incoming
data and deserialization. Similarly to Django's ``Form`` Serializers also providing validations of incoming
data to get valid and cleaned datatypes.


Declaring a Serializer and how it works
=======================================

Here is an example how Serializers are declared and working.


Declaring
---------

Object to use for this example:

.. code-block:: python

    from uuid import uuid4


    class Person(object):
        def __init__(name, age, email, oid=None):
            self.name = name
            self.age = age
            self.email = email
            self.oid = oid or uuid4()



    person = Person(name="Joe", age=20, email="me@example.com")


Declaring the Serializer

.. code-block:: python

    import aserializer


    class PersonSerializer(aserializer.Serializer):
        name = aserializer.StringField()
        age = aserializer.IntegerField()
        email = aserializer.EmailField()
        oid = aserializer.UUIDField()


Serializing
-----------

Serialize the Person object with the PersonSerializer:

.. code-block:: python

    serializer = PersonSerializer(person)
    serializer.name
    # Joe
    serializer.age
    # 20
    serializer.email
    # me@example.com
    serializer.oid
    # UUID('ad899890-e243-4103-80e0-09cea2a7fd5a')

Calling ``to_dict()`` you get a dictionary with Python datatypes

.. code-block:: python

    serializer.to_dict()
    # {'name': u'Joe', 'age': 20, 'email': u'me@example.com', 'oid': UUID('ad899890-e243-4103-80e0-09cea2a7fd5a')}


To serialize objects you need to call ``dump()`` to get a dictionary with naive datatypes.

.. code-block:: python

    serializer.dump()
    # {'name': u'Joe', 'age': 20, 'email': u'me@example.com', 'oid': u'ad899890-e243-4103-80e0-09cea2a7fd5a'}

The ``to_json()`` method returns the serialized object as json

.. code-block:: python

    serializer.to_json()
    # '{"name": "Joe", "age": 20, "email": "me@example.com", "oid": "ad899890-e243-4103-80e0-09cea2a7fd5a"}'


Deserializing
-------------

Deserializing is verry easy. It is almost the same like serializing:

.. code-block:: python

    data = '{"name": "Joe", "age": 20, "email": "me@example.com", "oid": "ad899890-e243-4103-80e0-09cea2a7fd5a"}'
    serializer = PersonSerializer(data)
    serializer.name
    # Joe
    serializer.age
    # 20
    serializer.email
    # me@example.com
    serializer.oid
    # UUID('ad899890-e243-4103-80e0-09cea2a7fd5a')
    serializer.to_dict()
    # {'name': u'Joe', 'age': 20, 'email': u'me@example.com', 'oid': UUID('ad899890-e243-4103-80e0-09cea2a7fd5a')}


Validation
----------

To validate the serialized or deserialzed incoming data you need to call ``is_valid()``.
On validation errors the ``.errors`` property representing the resulting error messages.


.. code-block:: python

    data = {"name": "Joe", "email": "me", "oid": "id"}
    serializer = PersonSerializer(data)
    serializer.is_valid()
    # False
    serializer.errors
    # {'age': u'This field is required.', 'email': u'Enter a valid email.', 'oid': u'Enter a valid uuid.'}


