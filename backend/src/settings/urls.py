from dataclasses import dataclass

@dataclass(frozen=True)
class BaseUrls:
    get_health = "get_health"


@dataclass(frozen=True)
class AppsUrls():
    pass


@dataclass(frozen=True)
class Urls(BaseUrls, AppsUrls):
    pass
