from db_monitor_api.alerting.notification.protocol import Notifier


class ChannelAlreadyRegisteredError(ValueError):
    def __init__(self, channel: str) -> None:
        super().__init__(f"Notifier channel already registered: {channel!r}")
        self.channel = channel


class UnknownChannelError(LookupError):
    def __init__(self, channel: str) -> None:
        super().__init__(f"Unknown notifier channel: {channel!r}")
        self.channel = channel


class ChannelRegistry:
    def __init__(self) -> None:
        self._channels: dict[str, Notifier] = {}

    def register(self, name: str, notifier: Notifier) -> None:
        if name in self._channels:
            raise ChannelAlreadyRegisteredError(name)
        self._channels[name] = notifier

    def replace(self, name: str, notifier: Notifier) -> None:
        self._channels[name] = notifier

    def unregister(self, name: str) -> None:
        self._channels.pop(name, None)

    def get(self, name: str) -> Notifier:
        notifier = self._channels.get(name)
        if notifier is None:
            raise UnknownChannelError(name)
        return notifier

    def has(self, name: str) -> bool:
        return name in self._channels

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._channels))
