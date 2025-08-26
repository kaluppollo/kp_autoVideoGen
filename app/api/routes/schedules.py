from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_schedules():
    # TODO: implement schedule listing
    return []