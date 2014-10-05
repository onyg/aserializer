# -*- coding: utf-8 -*-


class DjangoRequestMixin(object):

    def handle_extras(self, extras):
        request = extras.get('request', None)
        if request is None:
            return
        if not hasattr(request, 'GET'):
            return
        params = request.GET
        fields = params.get('fields', None)
        if fields is not None:
            if not isinstance(fields, (list, tuple,)):
                fields = fields.split(',')
            self._fields = fields
        exclude = params.get('exclude', None)
        if exclude is not None:
            if not isinstance(exclude, (list, tuple,)):
                exclude = exclude.split(',')
            self._exclude = exclude
        sort = params.get('sort', None)
        if sort is not None:
            if not isinstance(sort, (list, tuple,)):
                self._sort = sort.split(',')
        limit = params.get('limit', None)
        if limit is not None:
            try:
                self._limit = int(limit)
            except:
                pass
        offset = params.get('offset', None)
        if offset is not None:
            try:
                self._offset = int(offset)
            except:
                pass
