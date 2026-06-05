"""Unit of Work ContextVar behaviour (with a fake sessionmaker — no real DB)."""

from __future__ import annotations

import pytest

from infra.db.uow import SQLAlchemyUnitOfWork, get_current_session


class FakeSession:
    def __init__(self) -> None:
        self.committed = False
        self.rolledback = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolledback = True


class FakeSessionMaker:
    def __init__(self) -> None:
        self.session = FakeSession()

    def __call__(self):
        session = self.session

        class _Ctx:
            async def __aenter__(self):
                return session

            async def __aexit__(self, *exc):
                return False

        return _Ctx()


async def test_uow_sets_contextvar_and_commits():
    sm = FakeSessionMaker()
    uow = SQLAlchemyUnitOfWork(sm)  # type: ignore[arg-type]
    assert get_current_session() is None
    async with uow() as session:
        assert get_current_session() is session
    assert sm.session.committed is True
    assert get_current_session() is None


async def test_uow_rolls_back_on_error():
    sm = FakeSessionMaker()
    uow = SQLAlchemyUnitOfWork(sm)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        async with uow():
            raise ValueError("boom")
    assert sm.session.rolledback is True
    assert get_current_session() is None


async def test_uow_nested_reuses_outer_session():
    sm = FakeSessionMaker()
    uow = SQLAlchemyUnitOfWork(sm)  # type: ignore[arg-type]
    async with uow() as outer:
        async with uow() as inner:
            assert inner is outer
