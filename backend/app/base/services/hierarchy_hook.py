# from typing import Any, Required
#
# from app.base.repos.base import BaseRepository
# from app.base.services.base import BaseCreateHooks, BaseContextKwargs
# from app.features.memos.models import Memo
#
#
# class HierarchicalContextKwargs(BaseContextKwargs):
#     """Hierarchical context kwargs."""
#     parent_id: Required[str]
#
#
# class HierarchicalHooks(
#     BaseCreateHooks
# ):
#     parent_repo: BaseRepository
#
#     def _prepare_create_fields(self, obj_data, context: HierarchicalContextKwargs) -> dict[str, Any]:
#         base = super()._prepare_create_fields(obj_data, context)
#         parent_id = context["parent_id"]
#         if not self.parent_repo.get_by_pk(session, parent_id):
#             raise !!
#
#             return base
#         > prepare 대신에 preprocess 등으로 돌려야 함
#
# @order_by_for
# def order_by_title(desc: bool = True):
#     """
#     Order by title.
#     """
#     if desc:
#         return Memo.title.desc()
#     else:
#         return Memo.title.asc()