import os
import subprocess
import sys
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[3]
LOCUSTFILE = BACKEND_DIR / "load_tests" / "locustfile.py"
REQUIRED_ENVIRONMENT_VARIABLES = (
    "VOTING_LOAD_BASE_URL",
    "VOTING_POLL_ID",
    "VOTING_OPTION_ID",
)
TARGET_RPS = 10_000
TEST_DURATION_SECONDS = 120


@pytest.mark.performance
def test_open_poll_and_create_vote_sustain_10k_rps() -> None:
    missing_variables = [
        variable for variable in REQUIRED_ENVIRONMENT_VARIABLES if not os.getenv(variable)
    ]
    if missing_variables:
        pytest.skip(
            "Нагрузочный контур не настроен: " + ", ".join(missing_variables)
        )

    environment = os.environ | {"VOTING_TARGET_RPS": str(TARGET_RPS)}
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
        str(TARGET_RPS),
        "--spawn-rate",
        "2000",
        "--run-time",
        f"{TEST_DURATION_SECONDS}s",
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
        "Нагрузочный тест не достиг 10 000 RPS для обоих endpoint'ов "
        "или получил ошибки.\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )
