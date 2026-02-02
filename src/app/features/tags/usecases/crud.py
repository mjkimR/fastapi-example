from typing import Annotated

from fastapi import Depends

from app_base.base.services.base import BaseContextKwargs
from app_base.base.usecases.crud import BaseGetMultiUseCase, BaseGetUseCase
from app.features.tags.models import Tag
from app.features.tags.services import TagService


class GetTagUseCase(BaseGetUseCase[TagService, Tag, BaseContextKwargs]):
    def __init__(self, service: Annotated[TagService, Depends()]) -> None:
        super().__init__(service)


class GetMultiTagUseCase(BaseGetMultiUseCase[TagService, Tag, BaseContextKwargs]):
    def __init__(self, service: Annotated[TagService, Depends()]) -> None:
        super().__init__(service)
