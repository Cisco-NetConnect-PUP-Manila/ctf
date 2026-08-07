"""Service layer.

Business logic lives here rather than in route handlers so it can be driven directly from
tests -- notably the concurrency tests, which need N genuinely simultaneous transactions on
separate connections and cannot get that through TestClient.
"""
