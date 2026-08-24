from fastapi import FastAPI

app = FastAPI(
    title="EGD API Microservice",
    description="Microservice that connects to the European Go Database API for retrieving customized information",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Ok"}

#uv run uvicorn app.main:app --reload
#http://localhost:8000/docs