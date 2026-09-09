from dataclasses import dataclass

@dataclass(frozen=True)
class BaseUrls:
    get_health = "get_health"


@dataclass(frozen=True)
class AppsUrls():
    get_poll = "get_poll"
    get_admin_polls = "get_admin_polls"
    get_admin_poll_results = "get_admin_poll_results"
    create_admin_poll = "create_admin_poll"
    create_vote = "create_vote"


@dataclass(frozen=True)
class Urls(BaseUrls, AppsUrls):
    pass
