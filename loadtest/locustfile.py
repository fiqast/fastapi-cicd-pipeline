from locust import HttpUser, task, between, events


class ApiUser(HttpUser):
    wait_time = between(0.1, 0.5)

    @task(3)
    def health(self):
        self.client.get("/health")

    @task(1)
    def root(self):
        self.client.get("/")


P95_LIMIT_MS = 500
MAX_FAIL_RATIO = 0.01


@events.quitting.add_listener
def check_thresholds(environment, **kwargs):
    stats = environment.stats.total
    p95 = stats.get_response_time_percentile(0.95)
    if stats.fail_ratio > MAX_FAIL_RATIO:
        print(f"GATE FAILED: fail ratio {stats.fail_ratio:.2%} > {MAX_FAIL_RATIO:.2%}")
        environment.process_exit_code = 1
    elif p95 > P95_LIMIT_MS:
        print(f"GATE FAILED: p95 {p95}ms > {P95_LIMIT_MS}ms")
        environment.process_exit_code = 1
    else:
        print(f"GATE PASSED: p95 {p95}ms, fail ratio {stats.fail_ratio:.2%}")
        environment.process_exit_code = 0