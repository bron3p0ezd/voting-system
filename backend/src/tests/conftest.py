import os


for name, value in {
    "DB_HOST": "127.0.0.1",
    "DB_PORT": "5432",
    "DB_USER": "voting",
    "DB_PASS": "test-password",
    "DB_NAME": "voting_test",
    "ADMIN_LOGIN": "admin",
    "ADMIN_PASSWORD": "test-password",
    "ADMIN_JWT_SECRET": "test-admin-secret",
    "PARTICIPANT_JWT_SECRET": "test-participant-secret",
    "JWT_ALG": "HS256",
    "TEST_DB_HOST": "127.0.0.1",
    "TEST_DB_PORT": "5432",
    "TEST_DB_USER": "voting",
    "TEST_DB_PASS": "test-password",
    "TEST_DB_NAME": "voting_test",
    "TEST_ADMIN_JWT_SECRET": "test-admin-secret",
    "TEST_PARTICIPANT_JWT_SECRET": "test-participant-secret",
    "TEST_JWT_ALG": "HS256",
}.items():
    os.environ.setdefault(name, value)
