from starlette.responses import PlainTextResponse
from starlette.applications import Starlette
from starlette.endpoints import HTTPEndpoint
from starlette.routing import Route
from simple_api import SimpleApi
import models
import uvicorn


class Homepage(HTTPEndpoint):
    async def get(selt, request):
        return PlainTextResponse('Test starlette')


# app = Starlette(debug=True, routes=[Route('/', Homepage)])


app = SimpleApi(models)

if __name__ == '__main__':
    uvicorn.run(app.app)
