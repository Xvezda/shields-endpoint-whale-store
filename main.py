from fastapi import FastAPI
from whale_store import router


class CustomFastAPI(FastAPI):
    def include_router(self, router, **kwargs):
      prefix = kwargs.pop('prefix', '')
      super().include_router(router, prefix='/v1'+prefix, **kwargs)


app = CustomFastAPI()

@app.get('/', status_code=403)
async def read_root():
    return {'detail': 'Access Denied'}


app.include_router(
  router,
  prefix='/whale-store',
  tags=['whalestore']
)

