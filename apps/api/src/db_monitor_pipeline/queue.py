from collections import deque
from collections.abc import Callable
from typing import Protocol, cast

from db_monitor_api.auth.domain import utc_now
from db_monitor_pipeline.domain import CollectionJob

DEFAULT_QUEUE_NAME = "db-monitor:mysql-metrics"
REDIS_DEDUPE_SUFFIX = ":dedupe"
_ATOMIC_ENQUEUE_LUA = """
if redis.call('SADD', KEYS[2], ARGV[1]) == 0 then
  return 0
end
redis.call('RPUSH', KEYS[1], ARGV[2])
return 1
"""


class CollectionTaskQueue(Protocol):
    def dequeue(self) -> CollectionJob | None:
        ...

    def enqueue(self, job: CollectionJob) -> bool:
        ...


class InMemoryCollectionTaskQueue:
    def __init__(self) -> None:
        self._items: deque[CollectionJob] = deque()
        self._pending_keys: set[str] = set()

    def dequeue(self) -> CollectionJob | None:
        queue_length = len(self._items)
        now = utc_now()
        for _ in range(queue_length):
            job = self._items.popleft()
            if job.available_at > now:
                self._items.append(job)
                continue
            self._pending_keys.discard(job.dedupe_key)
            return job
        return None

    def enqueue(self, job: CollectionJob) -> bool:
        if job.dedupe_key in self._pending_keys:
            return False
        self._items.append(job)
        self._pending_keys.add(job.dedupe_key)
        return True

    def size(self) -> int:
        return len(self._items)


class RedisCollectionTaskQueue:
    def __init__(
        self,
        *,
        queue_name: str = DEFAULT_QUEUE_NAME,
        redis_url: str,
    ) -> None:
        import redis

        self._dedupe_name = f"{queue_name}{REDIS_DEDUPE_SUFFIX}"
        self._client = redis.Redis.from_url(redis_url, decode_responses=True)
        self._enqueue_script: Callable[[list[str], list[str]], int] = self._client.register_script(
            _ATOMIC_ENQUEUE_LUA
        )
        self._queue_name = queue_name

    def dequeue(self) -> CollectionJob | None:
        queue_length = int(cast(int, self._client.llen(self._queue_name)))
        for _ in range(queue_length):
            payload = cast(str | None, self._client.lpop(self._queue_name))
            if payload is None:
                return None
            job = CollectionJob.from_json(payload)
            if job.available_at > utc_now():
                self._client.rpush(self._queue_name, payload)
                continue
            self._client.srem(self._dedupe_name, job.dedupe_key)
            return job
        return None

    def enqueue(self, job: CollectionJob) -> bool:
        return bool(
            self._enqueue_script(
                [self._queue_name, self._dedupe_name],
                [job.dedupe_key, job.to_json()],
            )
        )
