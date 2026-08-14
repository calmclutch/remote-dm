from fastapi import FastAPI

app = FastAPI(title="RemoteDM API")


@app.get("/")
async def root():
    return {"status": "online", "service": "RemoteDM"}


@app.get("/health")
async def health():
    return {"status": "healthy"}