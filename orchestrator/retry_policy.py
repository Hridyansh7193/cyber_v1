from langgraph.types import RetryPolicy

def get_retry_policy() -> RetryPolicy:
    return RetryPolicy(
        initial_interval=1.0,
        backoff_factor=2.0,
        max_interval=10.0,
        max_attempts=3,
        retry_on=lambda exc: isinstance(exc, (TimeoutError, ConnectionError, OSError, RuntimeError))
    )
