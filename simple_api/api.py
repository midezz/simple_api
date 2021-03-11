from starlette.endpoints import HTTPEndpoint
from starlette.responses import JSONResponse, PlainTextResponse


class APIView(HTTPEndpoint):
    def __init__(self, model, session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.session = session


class CreateAPI(APIView):
    async def post(self, request):
        data = await request.json()
        session = self.session()
        model = self.model(**data)
        session.add(model)
        session.commit()
        values = self.model.get_columns_values(model)
        session.close()
        return JSONResponse(values)


class ListAPI(APIView):
    async def get(self, request):
        pass


class ListCreateAPI(ListAPI, CreateAPI):
    pass


class GetAPI(APIView):
    async def get(self, request):
        return PlainTextResponse(self.model.__name__)


class UpdateAPI(APIView):
    async def put(self, request):
        pass


class DeleteAPI(APIView):
    async def delete(self, request):
        pass


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
