"""Repository protocols (typing-only contracts).

Concrete implementations live in ``core/<domain>/repo.py`` and extend
``core.sqlalchemy_repo.SQLAlchemyRepo``.
"""

from __future__ import annotations

from typing import Protocol, TypeVar

E = TypeVar("E")


class NotFoundError(Exception):
    def __init__(self, entity: str, key: object) -> None:
        super().__init__(f"{entity} not found: {key!r}")
        self.entity = entity
        self.key = key


class ReadRepo(Protocol[E]):
    async def list(self) -> list[E]: ...


class WriteRepo(Protocol[E]):
    async def add(self, entity: E) -> E: ...
