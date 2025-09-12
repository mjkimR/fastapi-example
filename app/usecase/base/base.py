from abc import abstractmethod


class BaseUseCase:
    @abstractmethod
    async def execute(self, *args, **kwargs):
        raise NotImplementedError
