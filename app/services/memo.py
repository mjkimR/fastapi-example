from sqlalchemy.ext.asyncio import AsyncSession


class MemoService:
    def __init__(self, repo):
        self.repo = repo

    def get(self, session: AsyncSession):
        raise NotImplementedError

    def get_multi(self, session: AsyncSession):
        raise NotImplementedError

    def create(self, session: AsyncSession):
        raise NotImplementedError

    def update(self, session: AsyncSession):
        raise NotImplementedError

    def delete(self, session: AsyncSession):
        raise NotImplementedError
