from typing import Annotated

from fastapi import Depends

from app.models.tags import Tag
from app.services.tags import TagService
from app.usecase.base.crud import BaseGetMultiUseCase, BaseGetUseCase


class GetTagUseCase(BaseGetUseCase[TagService, Tag]):
    def __init__(self, service: Annotated[TagService, Depends()]) -> None:
        super().__init__(service)


class GetMultiTagUseCase(BaseGetMultiUseCase[TagService, Tag]):
    def __init__(self, service: Annotated[TagService, Depends()]) -> None:
        super().__init__(service)
