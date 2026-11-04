from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "hello v2"}


@app.get("/health")
def health():
    return {"status": "ok"}