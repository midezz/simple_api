from starlette.endpoints import HTTPEndpoint
from starlette.responses import PlainTextResponse


class APIView(HTTPEndpoint):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model


class CreateView(HTTPEndpoint):
    async def post(self, request):
        pass


class ListView(HTTPEndpoint):
    async def get(self, request):
        pass


class RetrieveView(APIView):
    async def get(self, request):
        return PlainTextResponse(self.model.__name__)
