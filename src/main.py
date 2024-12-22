from src.core.handler import register_app

app = register_app()


@app.middleware('http')
async def count_requests(request, call_next):
    response = await call_next(request)
    return response
