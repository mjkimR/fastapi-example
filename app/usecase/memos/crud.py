from typing import Annotated

from fastapi import Depends

from app.models.memos import Memo
from app.schemas.memos import MemoCreate, MemoUpdate
from app.services.memos import MemoService
from app.usecase.base.crud import (
    BaseGetUseCase,
    BaseGetMultiUseCase,
    BaseCreateUseCase,
    BaseUpdateUseCase,
    BaseDeleteUseCase,
)


class GetMemoUseCase(BaseGetUseCase[MemoService, Memo]):
    def __init__(self, service: Annotated[MemoService, Depends()]):
        super().__init__(service)


class GetMultiMemoUseCase(BaseGetMultiUseCase[MemoService, Memo]):
    def __init__(self, service: Annotated[MemoService, Depends()]):
        super().__init__(service)


class CreateMemoUseCase(BaseCreateUseCase[MemoService, Memo, MemoCreate]):
    def __init__(self, service: Annotated[MemoService, Depends()]):
        super().__init__(service)


class UpdateMemoUseCase(BaseUpdateUseCase[MemoService, Memo, MemoUpdate]):
    def __init__(self, service: Annotated[MemoService, Depends()]):
        super().__init__(service)


class DeleteMemoUseCase(BaseDeleteUseCase[MemoService, Memo]):
    def __init__(self, service: Annotated[MemoService, Depends()]):
        super().__init__(service)
