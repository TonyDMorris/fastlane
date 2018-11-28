from derpconf.config import Config

Config.allow_environment_variables()

Config.define("ENV", "development", "Environment application is running in", "General")
Config.define(
    "SECRET_KEY",
    "OTNDN0VCRDAtRTMyMS00NUM0LUFFQUYtNEI4QUE4RkFCRjUzCg==",
    "Secret key to use in flask.",
    "General",
)

Config.define(
    "REDIS_URL", "redis://localhost:10100/0", "Redis connection string", "Redis"
)

Config.define(
    "WORKER_SLEEP_TIME_MS",
    10,
    "Number of milliseconds that EasyQ must sleep before getting the next job",
    "Worker",
)

Config.define(
    "HARD_EXECUTION_TIMEOUT_SECONDS",
    30 * 60,
    "Number of seconds that EasyQ must wait before killing an execution",
    "Worker",
)

Config.define(
    "EXPONENTIAL_BACKOFF_MIN_MS",
    1000,
    "Number of milliseconds that EasyQ must wait before the first retry in each job",
    "Worker",
)

Config.define(
    "EXPONENTIAL_BACKOFF_FACTOR",
    2,
    "Factor to multiply backoff by in each retry",
    "Worker",
)

Config.define(
    "MAX_GLOBAL_SIMULTANEOUS_EXECUTIONS",
    2,
    "Maximum number of simultaneous executions across all executors",
    "Worker",
)

Config.define(
    "EXECUTOR",
    "easyq.worker.docker_executor",
    "Module full name where to find the Executor class",
    "Worker",
)

Config.define(
    "DOCKER_HOSTS",
    '[{"match": "", "hosts": ["localhost:2376"], "maxRunning":2}]',
    "Docker Hosts to add to pool",
    "Docker Executor",
)

Config.define(
    "MONGODB_SETTINGS",
    {
        "host": "localhost",
        "port": 10101,
        "db": "easyq",
        "serverSelectionTimeoutMS": 100,
        "connect": False,
    },
    "MongoDB socket timeout in ms",
    "Models",
)
