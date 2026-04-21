from typing import Protocol

from db_monitor_api.alerting.domain import NotificationRequest


class Notifier(Protocol):
    def send(self, request: NotificationRequest) -> None:
        ...


class InMemoryNotifier:
    def __init__(self) -> None:
        self.requests: list[NotificationRequest] = []

    def send(self, request: NotificationRequest) -> None:
        self.requests.append(request)
