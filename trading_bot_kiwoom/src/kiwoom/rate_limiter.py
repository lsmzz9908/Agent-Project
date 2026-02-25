from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field


@dataclass
class _Task:
    fn: callable
    retries: int
    done: threading.Event = field(default_factory=threading.Event)
    exc: Exception | None = None


class TrRateLimiter:
    def __init__(self, delay_sec: float = 0.25):
        self.delay_sec = delay_sec
        self.q: queue.Queue[_Task] = queue.Queue()
        self._stop = False
        self.worker = threading.Thread(target=self._run, daemon=True)
        self.worker.start()

    def submit(self, fn, retries: int = 2, wait: bool = False, timeout_sec: float = 5.0):
        task = _Task(fn=fn, retries=retries)
        self.q.put(task)
        if wait:
            if not task.done.wait(timeout=timeout_sec):
                raise TimeoutError("TR task timeout in rate limiter")
            if task.exc:
                raise task.exc
        return task

    def _run(self):
        while not self._stop:
            task = self.q.get()
            try:
                task.fn()
                task.done.set()
            except Exception as exc:
                if task.retries > 0:
                    task.retries -= 1
                    self.q.put(task)
                else:
                    task.exc = exc
                    task.done.set()
            time.sleep(self.delay_sec)

    def stop(self):
        self._stop = True
