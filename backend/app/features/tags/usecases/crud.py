from typing import Annotated

from fastapi import Depends

from app.features.tags.models import Tag
from app.base.services.base import BaseContextKwargs
from app.features.tags.services import TagService
from app.base.usecases.crud import BaseGetMultiUseCase, BaseGetUseCase


class GetTagUseCase(BaseGetUseCase[TagService, Tag, BaseContextKwargs]):
    def __init__(self, service: Annotated[TagService, Depends()]) -> None:
        super().__init__(service)


class GetMultiTagUseCase(BaseGetMultiUseCase[TagService, Tag, BaseContextKwargs]):
    def __init__(self, service: Annotated[TagService, Depends()]) -> None:
        super().__init__(service)
