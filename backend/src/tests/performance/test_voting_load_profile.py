import os
import subprocess
import sys
from dataclasses import dataclass
from math import ceil
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[3]
LOCUSTFILE = BACKEND_DIR / "load_tests" / "locustfile.py"
REQUIRED_ENVIRONMENT_VARIABLES = (
    "VOTING_LOAD_BASE_URL",
    "VOTING_POLL_ID",
    "VOTING_OPTION_ID",
)
MEASUREMENT_SECONDS = 60
MAX_ERROR_RATE = 0.001
MAX_P95_MILLISECONDS = 500
SPAWN_RATE = 100


@dataclass(frozen=True)
class LoadProfile:
    name: str
    target_vote_rps: int


LOAD_PROFILES = {
    "sustained": LoadProfile(name="sustained", target_vote_rps=1_667),
    "peak": LoadProfile(name="peak", target_vote_rps=8_000),
}


def get_load_profile() -> LoadProfile:
    profile_name = os.getenv("VOTING_LOAD_PROFILE", "sustained")
    try:
        return LOAD_PROFILES[profile_name]
    except KeyError:
        available_profiles = ", ".join(LOAD_PROFILES)
        pytest.fail(
            f"Неизвестный VOTING_LOAD_PROFILE={profile_name!r}. "
            f"Допустимые значения: {available_profiles}."
        )


@pytest.mark.performance
def test_voting_flow_meets_configured_load_profile() -> None:
    missing_variables = [
        variable for variable in REQUIRED_ENVIRONMENT_VARIABLES if not os.getenv(variable)
    ]
    if missing_variables:
        pytest.skip(
            "Нагрузочный контур не настроен: " + ", ".join(missing_variables)
        )

    profile = get_load_profile()
    startup_seconds = ceil(profile.target_vote_rps / SPAWN_RATE)
    run_time_seconds = startup_seconds + MEASUREMENT_SECONDS + 15
    environment = os.environ | {
        "VOTING_TARGET_VOTE_RPS": str(profile.target_vote_rps),
        "VOTING_MEASUREMENT_SECONDS": str(MEASUREMENT_SECONDS),
        "VOTING_MAX_ERROR_RATE": str(MAX_ERROR_RATE),
        "VOTING_MAX_P95_MILLISECONDS": str(MAX_P95_MILLISECONDS),
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
        str(profile.target_vote_rps),
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

    assert completed.returncode == 0, (
        f"Профиль {profile.name} не достиг {profile.target_vote_rps} успешных "
        "голосов/с, превысил error rate 0,1% или p95 500 мс.\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )
