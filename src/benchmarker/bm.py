"""
Benchmarker for the e2eeftp server.
"""

from pathlib import Path
from time import perf_counter
import threading


class BenchMark:
    """this is the benckmarker class used to benchmark.
    """
    def __init__(self, warmup: bool=True):
        self.warmup = warmup

    def _warmup(self):
        for i in range(100_000_000): ...

    def __enter__(self):
        print("Running warmup...")
        if self.warmup:
            self.start_warmup = perf_counter()
            self._warmup()
            self.end_warmup = perf_counter()
            self.duriation_warmup = self.end_warmup - self.start_warmup
            print(f"Warmup took: {self.duriation_warmup:.6f}s")
        print("Benckmarking function...")
        self.start = perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = perf_counter()
        self.duration = self.end - self.start
        print(f"benchmark: {self.duration:.6f}s")


def main():
    from e2eeftp.server import e2eeftp
    from e2eeftp.client import e2eeftpClient

    server = e2eeftp(logging=False)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    client = e2eeftpClient(logging=False)

    def server_test():
        try:
            result = client.hlist()
            print("hlist returned:", result)
        except Exception as exc:
            print("client error:", exc)

    try:
        print("with warmup:")
        with BenchMark() as bm:
            server_test()
        print("\nwithout warmup:")
        with BenchMark(warmup=False) as bm:
            server_test()
    except KeyboardInterrupt:
        print("benchmark interrupted")


if __name__ == "__main__":
    main()
