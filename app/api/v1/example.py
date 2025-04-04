from fastapi import APIRouter

router = APIRouter(prefix="/example", tags=["Example"])


@router.get("/", response_model=dict)
def get_hello():
    return {"message": "Hello World!"}
