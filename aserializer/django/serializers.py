# -*- coding: utf-8 -*-
import inspect

from aserializer.utils import py2to3, options
from aserializer.base import Serializer, SerializerBase
from aserializer import fields as serializer_fields
from aserializer.django import utils as django_utils
from aserializer.django.fields import RelatedManagerListSerializerField

try:
    from django.db import models as django_models
    MODEL_FIELD_MAPPING = {
        django_models.AutoField: serializer_fields.IntegerField,
        django_models.FloatField: serializer_fields.FloatField,
        django_models.PositiveIntegerField: serializer_fields.PositiveIntegerField,
        django_models.SmallIntegerField: serializer_fields.IntegerField,
        django_models.PositiveSmallIntegerField: serializer_fields.PositiveIntegerField,
        django_models.IntegerField: serializer_fields.IntegerField,
        django_models.DateTimeField: serializer_fields.DatetimeField,
        django_models.DateField: serializer_fields.DateField,
        django_models.TimeField: serializer_fields.TimeField,
        django_models.DecimalField: serializer_fields.DecimalField,
        django_models.EmailField: serializer_fields.EmailField,
        django_models.CharField: serializer_fields.StringField,
        django_models.URLField: serializer_fields.UrlField,
        django_models.SlugField: serializer_fields.StringField,
        django_models.TextField: serializer_fields.StringField,
        django_models.CommaSeparatedIntegerField: serializer_fields.StringField,
        django_models.BooleanField: serializer_fields.BooleanField,
        django_models.NullBooleanField: serializer_fields.BooleanField,
    }
    if django_utils.django_version >= (1, 8, 0):
        MODEL_FIELD_MAPPING[django_models.UUIDField] = serializer_fields.UUIDField
except ImportError:
    django_models = None
    MODEL_FIELD_MAPPING = {}


class DjangoModelSerializerBase(SerializerBase):

    def __new__(cls, name, bases, attrs):
        new_class = super(DjangoModelSerializerBase, cls).__new__(cls, name, bases, attrs)
        cls.set_fields_from_model(new_class=new_class,
                                  fields=new_class._base_fields,
                                  meta=new_class._meta)
        return new_class

    @classmethod
    def get_meta_options_cls(cls):
        return options.ModelSerializerMetaOptions

    @staticmethod
    def get_all_fieldnames(fields):
        result = []
        for name, field in fields.items():
            result.append(name)
            if field.map_field:
                result.append(field.map_field)
        return list(set(result))

    @classmethod
    def set_fields_from_model(cls, new_class, fields, meta):
        if django_models is None or meta.model is None:
            return
        meta.parents.handle(meta.model)
        all_field_names = cls.get_all_fieldnames(fields)
        for model_field in django_utils.get_local_fields(meta.model):
            if model_field.name not in all_field_names:
                serializer_field = cls.add_local_model_field(fields, model_field, meta=meta)
                if serializer_field:
                    setattr(new_class, model_field.name, serializer_field)
        for model_field in django_utils.get_related_fields(meta.model):
            if model_field.name not in all_field_names:
                serializer_field = cls.add_relation_model_field(fields, model_field, meta=meta)
                if serializer_field:
                    setattr(new_class, model_field.name, serializer_field)
        for model_field in django_utils.get_reverse_related_fields(meta.model):
            field_name = django_utils.get_reverse_related_name_from_field(model_field)
            if field_name not in all_field_names:
                serializer_field = cls.add_reverse_relation_model_field(fields, model_field, meta=meta)
                if serializer_field:
                    setattr(new_class, field_name, serializer_field)

    @staticmethod
    def get_field_class(model_field, mapping=None):
        if mapping is None:
            mapping = MODEL_FIELD_MAPPING
        for model in inspect.getmro(model_field.__class__):
            if model in mapping:
                return mapping[model]
        return None

    @staticmethod
    def get_nested_serializer_class(model_field, parent_manager=None, **field_arguments):
        class NestedModelSerializer(NestedDjangoModelSerializer):
            class Meta:
                model = model_field
                parents = parent_manager
                field_kwargs = field_arguments
        return NestedModelSerializer

    @classmethod
    def get_field_from_modelfield(cls, model_field, meta=None, **kwargs):
        field_class = cls.get_field_class(model_field)
        if model_field.primary_key:
            kwargs['identity'] = True
            kwargs['required'] = False
            kwargs['on_null'] = serializer_fields.HIDE_FIELD
        if model_field.null:
            kwargs['required'] = False
        if model_field.has_default():
            kwargs['default'] = model_field.get_default()
        if model_field.flatchoices:
            kwargs['choices'] = model_field.flatchoices
            if meta:
                kwargs = meta.field_arguments.parse(model_field.name, **kwargs)
            return serializer_fields.ChoiceField(**kwargs)
        if isinstance(model_field, django_models.CharField) and not isinstance(model_field, django_models.URLField):
            max_length = getattr(model_field, 'max_length', None)
            if max_length is not None:
                kwargs.update({'max_length': getattr(model_field, 'max_length')})
        elif isinstance(model_field, django_models.DecimalField):
            kwargs.update({'decimal_places': getattr(model_field, 'decimal_places')})
        if meta:
            kwargs = meta.field_arguments.parse(model_field.name, **kwargs)
        return field_class(**kwargs) if field_class else None

    @classmethod
    def add_local_model_field(cls, fields, model_field, meta, **kwargs):
        _field = cls.get_field_from_modelfield(model_field, meta=meta, **kwargs)
        if _field is not None:
            _field.add_name(model_field.name)
            fields[model_field.name] = _field
        return _field

    @classmethod
    def add_relation_model_field(cls, fields, model_field, meta, **kwargs):
        if django_utils.is_relation_field(model_field):
            relation_parents_manager = meta.parents.get_working_copy()
            rel_django_model = django_utils.get_related_model_from_field(model_field)
            if not relation_parents_manager.handle(rel_django_model):
                return None
            if model_field.primary_key:
                kwargs['identity'] = True
                kwargs['required'] = False
                kwargs['on_null'] = serializer_fields.HIDE_FIELD
            if model_field.null or model_field.blank:
                kwargs['required'] = False
            field_kwargs = meta.field_arguments.get_nested_field_kwargs(model_field.name)
            serializer_cls = cls.get_nested_serializer_class(rel_django_model,
                                                             relation_parents_manager,
                                                             **field_kwargs)
            if isinstance(model_field, django_models.ManyToManyField):
                field_class = RelatedManagerListSerializerField
            else:
                field_class = serializer_fields.SerializerField
            kwargs = meta.field_arguments.parse(model_field.name, **kwargs)
            _field = field_class(serializer_cls, **kwargs)
            _field.add_name(model_field.name)
            fields[model_field.name] = _field
            return _field
        return None

    @classmethod
    def add_reverse_relation_model_field(cls, fields, model_field, meta, **kwargs):
        if django_utils.is_reverse_relation_field(model_field):
            field_name = django_utils.get_reverse_related_name_from_field(model_field)
            relation_parents_manager = meta.parents.get_working_copy()
            rel_django_model = django_utils.get_related_model_from_field(model_field)
            if not relation_parents_manager.handle(rel_django_model):
                return None
            field_kwargs = meta.field_arguments.get_nested_field_kwargs(field_name)
            serializer_cls = cls.get_nested_serializer_class(rel_django_model,
                                                             relation_parents_manager,
                                                             **field_kwargs)
            if django_utils.is_reverse_one2one_relation_field(model_field):
                field_class = serializer_fields.SerializerField
            else:
                field_class = RelatedManagerListSerializerField
            kwargs = meta.field_arguments.parse(model_field.name, **kwargs)
            _field = field_class(serializer_cls, required=False, **kwargs)
            _field.add_name(django_utils.get_reverse_related_name_from_field(model_field))
            fields[field_name] = _field
            return _field
        return None


class NestedDjangoModelSerializer(py2to3.with_metaclass(DjangoModelSerializerBase, Serializer)):
    with_registry = False


class DjangoModelSerializer(py2to3.with_metaclass(DjangoModelSerializerBase, Serializer)):
    pass
