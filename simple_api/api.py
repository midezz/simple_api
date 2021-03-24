from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse

from simple_api import Session


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
            return JSONResponse({'error': True}, status_code=400)
        else:
            session.close()
            return JSONResponse(values, status_code=201)


class ListAPI(APIView):
    async def get(self, request):
        session = Session()
        validate_filters = self.model.valid_filters(request.query_params)
        if 'error' in validate_filters:
            session.close()
            return JSONResponse(validate_filters, status_code=400)
        filters = self.model.construct_filters(request.query_params)
        query = session.query(self.model).filter(*filters)
        result = [self.model.get_columns_values(model) for model in query.all()]
        session.close()
        if len(result) == 0:
            return JSONResponse({'error': 'Not found'}, status_code=404)
        return JSONResponse(result)


class ListCreateAPI(ListAPI, CreateAPI):
    pass


class GetAPI(APIView):
    async def get(self, request):
        session = Session()
        try:
            result = session.query(self.model).filter_by(**request.path_params).first()
        except Exception:
            session.close()
            return JSONResponse({'error': True}, status_code=400)
        session.close()
        if not result:
            return JSONResponse({'error': 'Not found'}, status_code=404)
        values = self.model.get_columns_values(result)
        return JSONResponse(values)


class UpdateAPI(APIView):
    async def put(self, request):
        pass


class DeleteAPI(APIView):
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


class GetUpdateDeleteAPI(GetAPI, UpdateAPI, DeleteAPI):
    pass


class UpdateDeleteAPI(UpdateAPI, DeleteAPI):
    pass


class GetDeleteAPI(GetAPI, DeleteAPI):
    pass


class GetUpdateAPI(GetAPI, UpdateAPI):
    pass


HANDLER_CLASS = {
    ('get',): UpdateDeleteAPI,
    ('delete', 'put'): GetAPI,
    ('delete',): GetUpdateAPI,
    ('get', 'put'): DeleteAPI,
    ('delete', 'get'): UpdateAPI,
    ('put',): GetDeleteAPI,
}

HANDLER_CLASS_LISTCREATE = {
    ('list', 'post'): ListCreateAPI,
    ('list',): ListAPI,
    ('post',): CreateAPI,
}

CLASSES_LISTCREATE = (ListCreateAPI, ListAPI, CreateAPI)
