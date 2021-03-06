from starlette.exceptions import HTTPException
from starlette.responses import PlainTextResponse
from starlette.routing import Route


class SimpleApiRouter(Route):
    def __init__(self, model, *args, **kwargs):
        self.model = model
        super().__init__(*args, **kwargs)

    async def handle(self, scope, receive, send):
        if self.methods and scope["method"] not in self.methods:
            if "app" in scope:
                raise HTTPException(status_code=405)
            else:
                response = PlainTextResponse("Method Not Allowed", status_code=405)
            await response(scope, receive, send)
        else:
            await self.app(self.model, scope, receive, send)
