from dataclasses import dataclass

@dataclass(frozen=True)
class BaseUrls:
    get_health = "get_health"


@dataclass(frozen=True)
class AppsUrls():
    get_poll = "get_poll"


@dataclass(frozen=True)
class Urls(BaseUrls, AppsUrls):
    pass
