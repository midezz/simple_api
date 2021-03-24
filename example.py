import uvicorn
from starlette.endpoints import HTTPEndpoint
from starlette.responses import PlainTextResponse

import models
from simple_api.main import SimpleApi


class Homepage(HTTPEndpoint):
    async def get(selt, request):
        return PlainTextResponse('Test starlette')


# app = Starlette(debug=True, routes=[Route('/', Homepage)])


app = SimpleApi(models, 'postgresql://pydantic_orm:123456@127.0.0.1/pydantic_test')

if __name__ == '__main__':
    uvicorn.run(app.app)
