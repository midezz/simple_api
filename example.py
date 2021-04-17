import os

import uvicorn


import models
from simple_api.main import SimpleApi


app = SimpleApi(models, os.environ['DB_URL'])

if __name__ == '__main__':
    uvicorn.run(app.app)
