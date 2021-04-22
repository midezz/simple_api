from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from . import Session
from .url_params import UrlParams


def check_allowed_methods(method):
    async def wrapper(self, request):
        if method.__name__ in self.model.ConfigEndpoint.denied_methods:
            return await self.method_not_allowed(request)
        else:
            return await method(self, request)

    return wrapper


class APIView(HTTPEndpoint):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model


class CreateAPI(APIView):
    async def post(self, request):
        data = await request.json()
        session = Session()
        try:
            model = self.model(**data)
            session.add(model)
            session.commit()
            values = self.model.get_columns_values(model)
        except Exception:
            session.close()
            return JSONResponse({'errors': ['Bad request']}, status_code=400)
        else:
            session.close()
            return JSONResponse(values, status_code=201)


class ListAPI(APIView):
    async def get(self, request):
        session = Session()
        params = UrlParams(self.model, request.query_params)
        if not params.is_valid():
            session.close()
            return JSONResponse({'errors': params.errors}, status_code=400)
        query = (
            session.query(self.model).filter(*params.filters).order_by(params.order_by)
        )
        offset = (params.page_param - 1) * self.model.ConfigEndpoint.pagination
        if params.limit_param is None:
            query = query.offset(offset).limit(self.model.ConfigEndpoint.pagination)
        else:
            if (
                params.limit_param <= offset + self.model.ConfigEndpoint.pagination
                and params.limit_param > offset
            ):
                limit = params.limit_param - offset
                query = query.offset(offset).limit(limit)
            elif params.limit_param > offset + self.model.ConfigEndpoint.pagination:
                query = query.offset(offset).limit(self.model.ConfigEndpoint.pagination)
            else:
                query = query.limit(0)
        result = [self.model.get_columns_values(model) for model in query.all()]
        session.close()
        return JSONResponse(result)


class ListCreateAPI(ListAPI, CreateAPI):
    pass


class GetUpdateDeleteAPI(APIView):
    @check_allowed_methods
    async def delete(self, request):
        session = Session()
        try:
            result = session.query(self.model).filter_by(**request.path_params).first()
            if not result:
                session.close()
                return JSONResponse({'error': 'Not found'}, status_code=404)
            session.delete(result)
            session.commit()
        except Exception:
            session.close()
            return JSONResponse({'error': True}, status_code=400)
        session.close()
        values = self.model.get_columns_values(result)
        return JSONResponse(values)

    @check_allowed_methods
    async def get(self, request):
        session = Session()
        try:
            result = session.query(self.model).filter_by(**request.path_params).first()
        except Exception:
            session.close()
            return JSONResponse({'errors': ['Bad request']}, status_code=400)
        session.close()
        if not result:
            return JSONResponse({'errors': ['Not found']}, status_code=404)
        values = self.model.get_columns_values(result)
        return JSONResponse(values)

    async def update(self, request):
        data = await request.json()
        session = Session()
        try:
            result = (
                session.query(self.model).filter_by(**request.path_params).update(data)
            )
            session.commit()
        except Exception:
            session.close()
            return JSONResponse({'errors': ['Bad request']}, status_code=400)
        session.close()
        if not result:
            return JSONResponse({'errors': ['Not found']}, status_code=404)
        values = request.path_params.copy()
        values.update(data)
        return JSONResponse(values)

    @check_allowed_methods
    async def put(self, request):
        return await self.update(request)

    @check_allowed_methods
    async def patch(self, request):
        return await self.update(request)


HANDLER_CLASS_LISTCREATE = {
    ('list', 'post'): ListCreateAPI,
    ('list',): ListAPI,
    ('post',): CreateAPI,
}

CLASSES_LISTCREATE = (ListCreateAPI, ListAPI, CreateAPI)
