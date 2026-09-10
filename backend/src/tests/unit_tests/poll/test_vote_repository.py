from uuid import uuid4

import pytest
from sqlalchemy.dialects import postgresql

from apps.poll.impls.repositories.vote_repository import VoteRepositoryImpl


class ResultStub:
    def one_or_none(self):
        return None


class SessionStub:
    def __init__(self) -> None:
        self.calls: list[tuple[object, dict[str, object]]] = []

    async def execute(self, statement: object, parameters: dict[str, object]) -> ResultStub:
        self.calls.append((statement, parameters))
        return ResultStub()


@pytest.mark.asyncio
async def test_create_uses_one_postgresql_statement_for_vote_and_selections() -> None:
    session = SessionStub()
    poll_id = uuid4()
    option_id = uuid4()
    repository = VoteRepositoryImpl(session)  # type: ignore[arg-type]

    vote = await repository.create(poll_id, "a" * 64, [option_id])

    assert vote is None, "Пустой результат должен означать, что голос не создан."
    assert len(session.calls) == 1, "Запись голоса должна выполнять один SQL round-trip."
    statement, parameters = session.calls[0]
    sql = str(statement.compile(dialect=postgresql.dialect()))
    assert "INSERT INTO votes" in sql, "Запрос должен создавать запись голоса."
    assert "ON CONFLICT" in sql and "DO NOTHING" in sql, (
        "Дедупликация должна оставаться атомарной."
    )
    assert "INSERT INTO vote_selections" in sql, "Запрос должен добавлять выбранные варианты."
    assert "poll_options" in sql, "Запрос должен проверять принадлежность вариантов опросу."
    assert parameters == {"option_ids": [option_id]}, "В запрос передаются выбранные варианты."
