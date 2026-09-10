import json
from datetime import datetime
from uuid import UUID

from redis.exceptions import RedisError

from apps.poll.caches import PollCache
from apps.poll.dtos import PollDTO, PollOptionDTO
from apps.poll.models import SelectionType
from settings.cache import CacheClient


class RedisPollCache(PollCache):
    def __init__(self, client: CacheClient, ttl_seconds: int) -> None:
        self.__client = client
        self.__ttl_seconds = ttl_seconds

    async def get(self, poll_id: UUID) -> PollDTO | None:
        try:
            payload = await self.__client.get(self.__key(poll_id))
        except RedisError:
            return None
        if payload is None:
            return None
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")

        try:
            return self.__deserialize(payload)
        except (KeyError, TypeError, ValueError):
            await self.__delete_corrupted_value(poll_id)
            return None

    async def set(self, poll: PollDTO) -> None:
        try:
            await self.__client.set(
                self.__key(poll.id),
                self.__serialize(poll),
                ex=self.__ttl_seconds,
            )
        except RedisError:
            return

    def __key(self, poll_id: UUID) -> str:
        return f"poll:public:{poll_id}"

    def __serialize(self, poll: PollDTO) -> str:
        return json.dumps(
            {
                "id": str(poll.id),
                "question": poll.question,
                "selection_type": poll.selection_type.value,
                "min_selections": poll.min_selections,
                "max_selections": poll.max_selections,
                "starts_at": poll.starts_at.isoformat(),
                "ends_at": poll.ends_at.isoformat(),
                "options": [
                    {
                        "id": str(option.id),
                        "text": option.text,
                        "position": option.position,
                    }
                    for option in poll.options
                ],
            },
            separators=(",", ":"),
        )

    def __deserialize(self, payload: str) -> PollDTO:
        value = json.loads(payload)
        if not isinstance(value, dict):
            raise ValueError("Кэш опроса должен содержать JSON-объект.")
        raw_options = value["options"]
        if not isinstance(raw_options, list):
            raise ValueError("В кэше опроса отсутствуют варианты ответа.")

        options: list[PollOptionDTO] = []
        for option in raw_options:
            if not isinstance(option, dict):
                raise ValueError("Вариант ответа в кэше имеет неверный формат.")
            options.append(
                PollOptionDTO(
                    id=UUID(str(option["id"])),
                    text=str(option["text"]),
                    position=int(option["position"]),
                )
            )
        return PollDTO(
            id=UUID(str(value["id"])),
            question=str(value["question"]),
            selection_type=SelectionType(str(value["selection_type"])),
            min_selections=int(value["min_selections"]),
            max_selections=int(value["max_selections"]),
            starts_at=datetime.fromisoformat(str(value["starts_at"])),
            ends_at=datetime.fromisoformat(str(value["ends_at"])),
            options=options,
        )

    async def __delete_corrupted_value(self, poll_id: UUID) -> None:
        try:
            await self.__client.delete(self.__key(poll_id))
        except RedisError:
            return
