import os
import time
from uuid import uuid4

from jwt import encode
from locust import HttpUser, constant_pacing, events, task
from locust.env import Environment


GET_ONLY_SCENARIO = "get_only"
POST_ONLY_SCENARIO = "post_only"
AVAILABLE_SCENARIOS = (GET_ONLY_SCENARIO, POST_ONLY_SCENARIO)

POLL_ID = os.environ["VOTING_POLL_ID"]
LOAD_SCENARIO = os.environ["VOTING_LOAD_SCENARIO"]
if LOAD_SCENARIO not in AVAILABLE_SCENARIOS:
    available_scenarios = ", ".join(AVAILABLE_SCENARIOS)
    raise RuntimeError(
        f"Неизвестный VOTING_LOAD_SCENARIO={LOAD_SCENARIO!r}. "
        f"Допустимые значения: {available_scenarios}."
    )

OPTION_ID = os.getenv("VOTING_OPTION_ID")
PARTICIPANT_JWT_SECRET = os.getenv("VOTING_PARTICIPANT_JWT_SECRET")
PARTICIPANT_JWT_ALGORITHM = os.getenv(
    "VOTING_PARTICIPANT_JWT_ALGORITHM",
    "HS256",
)
COOKIE_NAME = "participant_token"
GET_POLL_STAT = "get_poll"
CREATE_VOTE_STAT = "create_vote"
measurement_started_at: float | None = None
load_test_environment: Environment | None = None


class GetPollUser(HttpUser):
    abstract = LOAD_SCENARIO != GET_ONLY_SCENARIO
    wait_time = constant_pacing(1.0)

    @task
    def get_poll(self) -> None:
        self.client.cookies.clear()
        with self.client.get(
            f"/api/v1/polls/{POLL_ID}",
            name=GET_POLL_STAT,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Открытие опроса вернуло HTTP {response.status_code}")
                return
            if response.cookies.get(COOKIE_NAME) is None:
                response.failure("Открытие опроса не установило participant_token")


class CreateVoteUser(HttpUser):
    abstract = LOAD_SCENARIO != POST_ONLY_SCENARIO
    wait_time = constant_pacing(1.0)

    @task
    def create_vote(self) -> None:
        if OPTION_ID is None or PARTICIPANT_JWT_SECRET is None:
            raise RuntimeError("POST-only сценарий не получил обязательные настройки.")

        participant_token = encode(
            {"sub": str(uuid4())},
            PARTICIPANT_JWT_SECRET,
            algorithm=PARTICIPANT_JWT_ALGORITHM,
        )
        with self.client.post(
            f"/api/v1/polls/{POLL_ID}/votes",
            json={"option_ids": [OPTION_ID]},
            headers={"Cookie": f"{COOKIE_NAME}={participant_token}"},
            name=CREATE_VOTE_STAT,
            catch_response=True,
        ) as response:
            if response.status_code != 201:
                response.failure(f"Отправка голоса вернула HTTP {response.status_code}")


@events.test_start.add_listener
def remember_environment(environment: Environment, **_kwargs: object) -> None:
    global load_test_environment
    load_test_environment = environment


@events.spawning_complete.add_listener
def start_measurement(user_count: int, **_kwargs: object) -> None:
    global measurement_started_at
    if measurement_started_at is not None:
        return
    if load_test_environment is None:
        return

    load_test_environment.stats.reset_all()
    measurement_started_at = time.monotonic()


@events.quitting.add_listener
def report_throughput(environment: Environment, **_kwargs: object) -> None:
    if measurement_started_at is None:
        environment.process_exit_code = 1
        print("PERFORMANCE_RESULT measurement_not_started", flush=True)
        return

    measurement_duration = time.monotonic() - measurement_started_at
    stat_name, method = (
        (GET_POLL_STAT, "GET")
        if LOAD_SCENARIO == GET_ONLY_SCENARIO
        else (CREATE_VOTE_STAT, "POST")
    )
    stat = environment.stats.get(stat_name, method)
    successful_requests = stat.num_requests - stat.num_failures
    successful_rps = successful_requests / measurement_duration
    error_rate = (
        stat.num_failures / stat.num_requests
        if stat.num_requests
        else 0.0
    )
    p95_milliseconds = (
        stat.get_response_time_percentile(0.95)
        if stat.num_requests
        else 0
    )

    print(
        "PERFORMANCE_RESULT "
        f"scenario={LOAD_SCENARIO} "
        f"successful_requests={successful_requests} "
        f"measurement_seconds={measurement_duration:.2f} "
        f"successful_rps={successful_rps:.2f} "
        f"error_rate={error_rate:.4%} "
        f"p95_ms={p95_milliseconds}",
        flush=True,
    )
