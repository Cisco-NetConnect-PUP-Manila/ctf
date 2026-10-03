from concurrent.futures import ThreadPoolExecutor
from threading import Barrier


def test_concurrent_failures_cannot_bypass_account_budget(client):
    barrier = Barrier(6)

    def attempt(_):
        barrier.wait(timeout=10)
        return client.post('/auth/login', json={'email': 'unknown@example.com', 'password': 'wrong'}).status_code

    with ThreadPoolExecutor(max_workers=6) as pool:
        statuses = list(pool.map(attempt, range(6)))
    assert sorted(statuses) == [401, 401, 401, 401, 401, 429]
