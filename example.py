import uvicorn
from starlette.endpoints import HTTPEndpoint
from starlette.responses import PlainTextResponse

import models
from simple_api import SimpleApi


class Homepage(HTTPEndpoint):
    async def get(selt, request):
        return PlainTextResponse('Test starlette')


# app = Starlette(debug=True, routes=[Route('/', Homepage)])


app = SimpleApi(models)

if __name__ == '__main__':
    uvicorn.run(app.app)
