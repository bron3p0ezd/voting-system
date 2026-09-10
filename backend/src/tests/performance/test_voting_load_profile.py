import os
import subprocess
import sys
from math import ceil
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[3]
LOCUSTFILE = BACKEND_DIR / "load_tests" / "locustfile.py"
COMMON_REQUIRED_ENVIRONMENT_VARIABLES = (
    "VOTING_LOAD_BASE_URL",
    "VOTING_POLL_ID",
)
POST_REQUIRED_ENVIRONMENT_VARIABLES = (
    "VOTING_OPTION_ID",
    "VOTING_PARTICIPANT_JWT_SECRET",
)
MEASUREMENT_SECONDS = 60
SPAWN_RATE = 100
USER_COUNT = 1_667
GET_ONLY_SCENARIO = "get_only"
POST_ONLY_SCENARIO = "post_only"


def run_load_test(scenario: str, required_variables: tuple[str, ...]) -> None:
    missing_variables = [
        variable for variable in required_variables if not os.getenv(variable)
    ]
    if missing_variables:
        pytest.skip(
            "Нагрузочный контур не настроен: " + ", ".join(missing_variables)
        )

    startup_seconds = ceil(USER_COUNT / SPAWN_RATE)
    run_time_seconds = startup_seconds + MEASUREMENT_SECONDS
    environment = os.environ | {
        "VOTING_LOAD_SCENARIO": scenario,
    }
    command = [
        sys.executable,
        "-m",
        "locust",
        "--headless",
        "--only-summary",
        "--host",
        environment["VOTING_LOAD_BASE_URL"],
        "--locustfile",
        str(LOCUSTFILE),
        "--users",
        str(USER_COUNT),
        "--spawn-rate",
        str(SPAWN_RATE),
        "--run-time",
        f"{run_time_seconds}s",
    ]
    completed = subprocess.run(
        command,
        cwd=BACKEND_DIR,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    print(completed.stdout, end="")
    print(completed.stderr, end="", file=sys.stderr)

    if completed.returncode != 0:
        pytest.fail(
            f"Locust не смог завершить сценарий {scenario}. "
            f"Код возврата: {completed.returncode}."
        )


@pytest.mark.performance
def test_get_poll_reports_throughput() -> None:
    run_load_test(GET_ONLY_SCENARIO, COMMON_REQUIRED_ENVIRONMENT_VARIABLES)


@pytest.mark.performance
def test_create_vote_reports_throughput() -> None:
    run_load_test(
        POST_ONLY_SCENARIO,
        COMMON_REQUIRED_ENVIRONMENT_VARIABLES
        + POST_REQUIRED_ENVIRONMENT_VARIABLES,
    )
