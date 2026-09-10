import os
import time

from locust import HttpUser, constant_pacing, events, task
from locust.env import Environment


POLL_ID = os.environ["VOTING_POLL_ID"]
OPTION_ID = os.environ["VOTING_OPTION_ID"]
TARGET_VOTE_RPS = float(os.environ["VOTING_TARGET_VOTE_RPS"])
MEASUREMENT_SECONDS = float(os.environ["VOTING_MEASUREMENT_SECONDS"])
MAX_ERROR_RATE = float(os.environ.get("VOTING_MAX_ERROR_RATE", "0.001"))
MAX_P95_MILLISECONDS = int(os.environ.get("VOTING_MAX_P95_MILLISECONDS", "500"))
COOKIE_NAME = "participant_token"
OPEN_POLL_STAT = "open_poll"
CREATE_VOTE_STAT = "create_vote"
measurement_started_at: float | None = None
load_test_environment: Environment | None = None


class VotingUser(HttpUser):
    wait_time = constant_pacing(1.0)

    @task
    def open_poll_and_create_vote(self) -> None:
        self.client.cookies.clear()
        with self.client.get(
            f"/api/v1/polls/{POLL_ID}",
            name=OPEN_POLL_STAT,
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Открытие опроса вернуло HTTP {response.status_code}")
                return

            participant_token = response.cookies.get(COOKIE_NAME)
            if participant_token is None:
                response.failure("Открытие опроса не установило participant_token")
                return

        self.client.cookies.clear()
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
def remember_environment(environment, **_kwargs: object) -> None:
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
def verify_target_rps(environment, **_kwargs: object) -> None:
    if measurement_started_at is None:
        environment.process_exit_code = 1
        return

    measurement_duration = time.monotonic() - measurement_started_at
    if measurement_duration < MEASUREMENT_SECONDS:
        environment.process_exit_code = 1
        return

    for name, method in ((OPEN_POLL_STAT, "GET"), (CREATE_VOTE_STAT, "POST")):
        stat = environment.stats.get(name, method)
        if not stat.num_requests:
            environment.process_exit_code = 1
            continue
        error_rate = stat.num_failures / stat.num_requests
        if error_rate > MAX_ERROR_RATE:
            environment.process_exit_code = 1
            continue
        if stat.get_response_time_percentile(0.95) > MAX_P95_MILLISECONDS:
            environment.process_exit_code = 1

    vote_stat = environment.stats.get(CREATE_VOTE_STAT, "POST")
    successful_vote_rps = (
        (vote_stat.num_requests - vote_stat.num_failures) / measurement_duration
    )
    if successful_vote_rps < TARGET_VOTE_RPS:
        environment.process_exit_code = 1
