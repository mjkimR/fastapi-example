from app_base.base.repos.base import BaseRepository

# FastAPI Project Structure Guide for LLMs

This document outlines the architecture of the project and provides a step-by-step guide for adding new features. The goal is to enable an LLM to understand the patterns and conventions, and then autonomously create new, similar features.

## 1. Core Concepts & Architecture

The project follows a layered, modular, and feature-driven architecture.

- **`src/app_base/core`**: Contains application-wide components.
  - **`config.py`**: Manages environment variables and application settings.
  - **`database/`**: Handles database engine creation, session management (`get_session`), and transaction handling (`AsyncTransaction`).
  - **`logger.py`**: Configures application-wide logging.
  - **`middlewares/`**: Contains global middleware like CORS and request ID handling.
- **`src/app_base/base`**: Provides a set of reusable, generic building blocks for features. This is the "framework" of the application.
  - **`models`**: SQLAlchemy model mixins (`UUIDMixin`, `TimestampMixin`, `AuditMixin`) for common fields.
  - **`repos`**: A generic `BaseRepository` that provides a standard interface for database operations (CRUD).
  - **`schemas`**: Pydantic schema mixins for consistent API data shapes.
  - **`services`**: A powerful, hook-based service layer. Services orchestrate repositories and implement business logic through inheritable mixins.
  - **`usecases`**: The use case layer, which is injected into API endpoints. It wraps service calls within a database transaction (`AsyncTransaction`) and prepares the final response.
  - **`deps`**: Reusable FastAPI dependencies for common tasks like pagination, filtering, and ordering.
- **`src/app/features`**: Each subdirectory here represents a distinct feature or domain of the application (e.g., `workspaces`, `memos`, `tags`).

### Architectural Flow

A typical request flows through the application as follows:

1.  **API Endpoint (`features/.../api/v1.py`)**: Receives the HTTP request.
2.  **Dependency Injection**: FastAPI injects a **Use Case** into the endpoint.
3.  **Use Case (`features/.../usecases/crud.py`)**:
    -   Starts a database transaction (`AsyncTransaction`).
    -   Calls one or more **Services** to perform the required actions.
    -   Commits or rolls back the transaction.
4.  **Service (`features/.../services.py`)**:
    -   Orchestrates one or more **Repositories**.
    -   Uses a hook-based system (`_context_*`, `_prepare_*`, `_post_*`) to add behavior like validation, authorization, and side effects.
    -   Inherits functionality from `app/base/services/` mixins (e.g., `UserAwareHooksMixin`, `NestedResourceHooksMixin`).
5.  **Repository (`features/.../repos.py`)**:
    -   Inherits from `app/base/repos/base.py`.
    -   Interacts directly with the database using SQLAlchemy ORM.
6.  **Model (`features/.../models.py`)**:
    -   Defines the SQLAlchemy table schema.
    -   Inherits from `app/base/models/mixin.py` for common columns.

---

## 2. How to Add a New Feature

Follow these steps to add a new feature. We will use the example of adding "Comments" to a "Memo". A "Comment" is a child resource of a "Memo".

### Step 1: Create the Feature Directory

Create a new directory for your feature inside `src/app/features/`.

```
src/app/features/comments/
```

Inside this directory, create the standard file structure:

```
comments/
├── __init__.py
├── api/
│   ├── __init__.py
│   └── v1.py
├── models.py
├── repos.py
├── schemas.py
├── services.py
└── usecases/
    ├── __init__.py
    └── crud.py
```

### Step 2: `models.py` - Define the SQLAlchemy Model

Create the `Comment` model. It must inherit from the base mixins and define its specific columns and relationships.

-   **Parent Resource**: `Memo`
-   **Child Resource**: `Comment`

**File: `src/app/features/comments/models.py`**
```python
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app_base.base.models.mixin import Base, UUIDMixin, TimestampMixin, AuditMixin

if TYPE_CHECKING:
    from app.features.memos.models import Memo

class Comment(Base, UUIDMixin, TimestampMixin, AuditMixin):
    __tablename__ = "comments"

    contents: Mapped[str] = mapped_column()

    # Foreign Key to the parent (Memo)
    memo_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("memos.id"), nullable=False)
    memo: Mapped["Memo"] = relationship(back_populates="comments")
```
> **Note:** You also need to update the parent `Memo` model in `src/app/features/memos/models.py` to add the `comments` relationship.
> ```python
> # In memos/models.py, inside the Memo class
> comments: Mapped[List["Comment"]] = relationship(back_populates="memo", cascade="all, delete-orphan")
> ```

### Step 3: `schemas.py` - Define Pydantic Schemas

Create the Pydantic schemas for API validation and serialization.

**File: `src/app/features/comments/schemas.py`**
```python
import uuid
from pydantic import BaseModel, ConfigDict, Field
from app_base.base.schemas.mixin import UUIDSchemaMixin, TimestampSchemaMixin

class CommentCreate(BaseModel):
    contents: str = Field(..., description="The contents of the comment.")

class CommentUpdate(BaseModel):
    contents: str | None = Field(default=None, description="The contents of the comment.")

class CommentRead(UUIDSchemaMixin, TimestampSchemaMixin, BaseModel):
    contents: str = Field(..., description="The contents of the comment.")
    memo_id: uuid.UUID = Field(..., description="The memo id of the comment.")

    model_config = ConfigDict(from_attributes=True)
```

### Step 4: `repos.py` - Create the Repository

Create a repository for the `Comment` model. It's usually a simple class that inherits from `BaseRepository` and specifies the model.

**File: `src/app/features/comments/repos.py`**
```python
from app_base.base.repos.base import BaseRepository
from app.features.comments.models import Comment
from app.features.comments.schemas import CommentCreate, CommentUpdate

class CommentRepository(BaseRepository[Comment, CommentCreate, CommentUpdate]):
    model = Comment
```

### Step 5: `services.py` - Create the Service

The service class is the core of the feature's logic. It inherits from various mixins to gain functionality.

**File: `src/app/features/comments/services.py`**
```python
from typing import Annotated
from fastapi import Depends

from app_base.base.services.base import (
    BaseCreateServiceMixin, BaseGetServiceMixin, BaseGetMultiServiceMixin,
    BaseUpdateServiceMixin, BaseDeleteServiceMixin
)
from app_base.base.services.exists_check_hook import ExistsCheckHooksMixin
from app_base.base.services.user_aware_hook import UserAwareHooksMixin, UserContextKwargs
from app_base.base.services.nested_resource_hook import NestedResourceHooksMixin, NestedResourceContextKwargs
from app.features.comments.models import Comment
from app.features.comments.repos import CommentRepository
from app.features.comments.schemas import CommentCreate, CommentUpdate
from app.features.memos.repos import MemoRepository

# 1. Define the context Kwargs by combining required contexts
class CommentContextKwargs(NestedResourceContextKwargs, UserContextKwargs):
    pass

# 2. Create the service by inheriting from the required mixins
class CommentService(
    NestedResourceHooksMixin,
    UserAwareHooksMixin,
    ExistsCheckHooksMixin,
    BaseCreateServiceMixin[CommentRepository, Comment, CommentCreate, CommentContextKwargs],
    BaseGetMultiServiceMixin[CommentRepository, Comment, CommentContextKwargs],
    BaseGetServiceMixin[CommentRepository, Comment, CommentContextKwargs],
    BaseUpdateServiceMixin[CommentRepository, Comment, CommentUpdate, CommentContextKwargs],
    BaseDeleteServiceMixin[CommentRepository, Comment, CommentContextKwargs],
):
    def __init__(
            self,
            repo: Annotated[CommentRepository, Depends()],
            parent_repo: Annotated[MemoRepository, Depends()] # The parent's repository
    ):
        self._repo = repo
        self._parent_repo = parent_repo
    
    @property
    def repo(self) -> CommentRepository:
        return self._repo
        
    @property
    def parent_repo(self) -> MemoRepository:
        return self._parent_repo
        
    @property
    def context_model(self):
        return CommentContextKwargs
        
    @property
    def fk_name(self) -> str:
        return "memo_id"
```

### Step 6: `usecases/crud.py` - Create Use Cases

Use cases wrap service calls in a transaction. For simple CRUD, you can inherit from the base use cases.

**File: `src/app/features/comments/usecases/crud.py`**
```python
from typing import Annotated
from fastapi import Depends

from app.features.comments.models import Comment
from app.features.comments.schemas import CommentCreate, CommentUpdate
from app.features.comments.services import CommentService, CommentContextKwargs
from app.base.usecases.crud import (
    BaseGetUseCase,
    BaseGetMultiUseCase,
    BaseCreateUseCase,
    BaseUpdateUseCase,
    BaseDeleteUseCase
)

class GetCommentUseCase(BaseGetUseCase[CommentService, Comment, CommentContextKwargs]):
    def __init__(self, service: Annotated[CommentService, Depends()]) -> None:
        super().__init__(service)

class GetMultiCommentUseCase(BaseGetMultiUseCase[CommentService, Comment, CommentContextKwargs]):
    def __init__(self, service: Annotated[CommentService, Depends()]) -> None:
        super().__init__(service)

class CreateCommentUseCase(BaseCreateUseCase[CommentService, Comment, CommentCreate, CommentContextKwargs]):
    def __init__(self, service: Annotated[CommentService, Depends()]) -> None:
        super().__init__(service)

class UpdateCommentUseCase(BaseUpdateUseCase[CommentService, Comment, CommentUpdate, CommentContextKwargs]):
    def __init__(self, service: Annotated[CommentService, Depends()]) -> None:
        super().__init__(service)

class DeleteCommentUseCase(BaseDeleteUseCase[CommentService, Comment, CommentContextKwargs]):
    def __init__(self, service: Annotated[CommentService, Depends()]) -> None:
        super().__init__(service)
```

### Step 7: `api/v1.py` - Create API Endpoints

Define the FastAPI router and its endpoints. This is the entry point for your feature.

**File: `src/app/features/comments/api/v1.py`**
```python
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Body, status

from app_base.base.deps.params.page import PaginationParam
from app_base.base.exceptions.basic import NotFoundException
from app_base.base.schemas.paginated import PaginatedList
from app.features.auth.deps import get_current_user
from app.features.auth.models import User
from app.features.comments.schemas import CommentRead, CommentUpdate, CommentCreate
from app.features.comments.usecases.crud import (
    CreateCommentUseCase, GetMultiCommentUseCase, GetCommentUseCase,
    UpdateCommentUseCase, DeleteCommentUseCase
)

# The prefix is nested under the parent resource
router = APIRouter(
    prefix="/memos/{memo_id}/comments",
    tags=["Comments"],
    dependencies=[Depends(get_current_user)]
)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=CommentRead)
async def create_comment(
        use_case: Annotated[CreateCommentUseCase, Depends()],
        memo_id: uuid.UUID, # Path parameter from parent
        current_user: Annotated[User, Depends(get_current_user)],
        comment_in: CommentCreate = Body(),
):
    # Pass path parameters and user info via the context dictionary
    context = {"parent_id": memo_id, "user_id": current_user.id}
    return await use_case.execute(comment_in, context=context)

@router.get("", response_model=PaginatedList[CommentRead])
async def get_comments(
        use_case: Annotated[GetMultiCommentUseCase, Depends()],
        memo_id: uuid.UUID,
        current_user: Annotated[User, Depends(get_current_user)],
        pagination: PaginationParam,
):
    context = {"parent_id": memo_id, "user_id": current_user.id}
    return await use_case.execute(**pagination, context=context)

# ... Implement GET (single), PUT, and DELETE endpoints similarly ...

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        use_case: Annotated[DeleteCommentUseCase, Depends()],
        memo_id: uuid.UUID,
        current_user: Annotated[User, Depends(get_current_user)],
        comment_id: uuid.UUID,
):
    context = {"parent_id": memo_id, "user_id": current_user.id}
    if not await use_case.execute(comment_id, context=context):
        raise NotFoundException()
```

### Step 8: `__init__.py` and Main Router

Export the router from the `api` directory and include it in the main application router.

**File: `src/app/features/comments/api/__init__.py`**
```python
from .v1 import router as v1_comments_router

__all__ = ["v1_comments_router"]
```

**File: `src/app/router.py`**
```python
# ... other imports
from app.features.comments.api import v1_comments_router

# ...
# Feature routers
v1_router.include_router(v1_admin_router)
# ... other routers
v1_router.include_router(v1_tags_router)
v1_router.include_router(v1_comments_router) # Add the new router here

router.include_router(v1_router)
```

### Step 9: Create Database Migration

Finally, generate and apply the database migration for the new `comments` table using `alembic`.

```shell
# (Assuming alembic is configured)
alembic revision --autogenerate -m "feat: add comments table"
alembic upgrade head
```

This completes the process of adding a new, fully integrated feature that follows the project's established conventions.
