import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.memos import Memo
from app.schemas.base import PaginatedList
from app.schemas.memos import MemoCreate, MemoUpdate
from app.usecase.memos.crud import (
    CreateMemoUseCase,
    GetMemoUseCase,
    GetMultiMemoUseCase,
    UpdateMemoUseCase,
    DeleteMemoUseCase,
)


@pytest.fixture
def mock_memo_service():
    """Fixture for a mock memo service."""
    return AsyncMock()


@pytest.fixture
def mock_session():
    """Fixture for a mock session."""
    return MagicMock()


@pytest.fixture(autouse=True)
def patch_async_transaction(mocker, mock_session):
    """Fixture to patch AsyncTransaction for all tests in this module."""
    mock_async_transaction = mocker.patch("app.usecase.base.crud.AsyncTransaction")
    mock_async_transaction.return_value.__aenter__.return_value = mock_session
    return mock_async_transaction


@pytest.mark.asyncio
async def test_create_memo_use_case(mock_memo_service, mock_session):
    """
    Test CreateMemoUseCase
    - GIVEN a mock memo service and memo data
    - WHEN the execute method is called
    - THEN it should call the service's create method and return a memo
    """
    # GIVEN
    memo_data = MemoCreate(category="Test Category", title="Test Title", contents="Test Contents")
    expected_memo = Memo(id=uuid.uuid4(), category="Test Category", title="Test Title", contents="Test Contents")
    mock_memo_service.create.return_value = expected_memo

    create_memo_use_case = CreateMemoUseCase(service=mock_memo_service)

    # WHEN
    result = await create_memo_use_case.execute(obj_data=memo_data)

    # THEN
    mock_memo_service.create.assert_called_once_with(mock_session, memo_data)
    assert result == expected_memo


@pytest.mark.asyncio
async def test_get_memo_use_case(mock_memo_service, mock_session):
    """
    Test GetMemoUseCase
    - GIVEN a mock memo service and a memo ID
    - WHEN the execute method is called
    - THEN it should call the service's get method and return a memo
    """
    # GIVEN
    memo_id = uuid.uuid4()
    expected_memo = Memo(id=memo_id, category="Test", title="Test Title", contents="Test Contents")
    mock_memo_service.get.return_value = expected_memo

    get_memo_use_case = GetMemoUseCase(service=mock_memo_service)

    # WHEN
    result = await get_memo_use_case.execute(obj_id=memo_id)

    # THEN
    mock_memo_service.get.assert_called_once_with(mock_session, memo_id)
    assert result == expected_memo


@pytest.mark.asyncio
async def test_get_multi_memo_use_case(mock_memo_service, mock_session):
    """
    Test GetMultiMemoUseCase
    - GIVEN a mock memo service and pagination/filter parameters
    - WHEN the execute method is called
    - THEN it should call the service's get_multi method and return a list of memos
    """
    # GIVEN
    memos = [Memo(id=uuid.uuid4(), category="Test", title=f"Title {i}", contents=f"Contents {i}") for i in range(3)]
    expected_paginated_list = PaginatedList(items=memos, total=len(memos), offset=0, limit=10)
    mock_memo_service.get_multi.return_value = expected_paginated_list

    get_multi_memo_use_case = GetMultiMemoUseCase(service=mock_memo_service)
    params = {"offset": 0, "limit": 10, "order_by": ["-created_at"], "where": "{}"}

    # WHEN
    result = await get_multi_memo_use_case.execute(**params)

    # THEN
    mock_memo_service.get_multi.assert_called_once_with(mock_session, **params)
    assert result == expected_paginated_list


@pytest.mark.asyncio
async def test_update_memo_use_case(mock_memo_service, mock_session):
    """
    Test UpdateMemoUseCase
    - GIVEN a mock memo service, a memo ID, and update data
    - WHEN the execute method is called
    - THEN it should call the service's update method and return the updated memo
    """
    # GIVEN
    memo_id = uuid.uuid4()
    update_data = MemoUpdate(title="Updated Title", contents="Updated Contents")
    expected_updated_memo = Memo(id=memo_id, category="Test", title="Updated Title", contents="Updated Contents")
    mock_memo_service.update.return_value = expected_updated_memo

    update_memo_use_case = UpdateMemoUseCase(service=mock_memo_service)

    # WHEN
    result = await update_memo_use_case.execute(obj_id=memo_id, obj_data=update_data)

    # THEN
    mock_memo_service.update.assert_called_once_with(mock_session, memo_id, update_data)
    assert result == expected_updated_memo


@pytest.mark.asyncio
async def test_delete_memo_use_case(mock_memo_service, mock_session):
    """
    Test DeleteMemoUseCase
    - GIVEN a mock memo service and a memo ID
    - WHEN the execute method is called
    - THEN it should call the service's delete method
    """
    # GIVEN
    memo_id = uuid.uuid4()
    mock_memo_service.delete.return_value = None  # Or whatever the service returns

    delete_memo_use_case = DeleteMemoUseCase(service=mock_memo_service)

    # WHEN
    await delete_memo_use_case.execute(obj_id=memo_id)

    # THEN
    mock_memo_service.delete.assert_called_once_with(mock_session, memo_id)