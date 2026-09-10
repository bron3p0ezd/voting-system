import os

from locust import HttpUser, constant_pacing, events, task


POLL_ID = os.environ["VOTING_POLL_ID"]
OPTION_ID = os.environ["VOTING_OPTION_ID"]
TARGET_RPS = float(os.environ.get("VOTING_TARGET_RPS", "10000"))
COOKIE_NAME = "participant_token"
OPEN_POLL_STAT = "open_poll"
CREATE_VOTE_STAT = "create_vote"


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


@events.quitting.add_listener
def verify_target_rps(environment, **_kwargs: object) -> None:
    for name, method in ((OPEN_POLL_STAT, "GET"), (CREATE_VOTE_STAT, "POST")):
        stat = environment.stats.get(name, method)
        if stat.num_failures:
            environment.process_exit_code = 1
            continue
        if stat.current_rps < TARGET_RPS:
            environment.process_exit_code = 1
