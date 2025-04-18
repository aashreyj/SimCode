from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..constants import LANG_CONFIG_MAP
from ..models.code import Code
from ..service.execution_service import execute_code

router = APIRouter()

"""
This endpoint is used to execute user code in a sandboxed environment.
"""
@router.post("/execute")
async def run_code(code: Code):
    if code.language not in LANG_CONFIG_MAP.keys():
        return JSONResponse({"message": "Language not supported"}, status_code=400)

    return execute_code(code)
