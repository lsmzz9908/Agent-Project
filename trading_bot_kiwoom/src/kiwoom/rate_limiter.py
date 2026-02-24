from __future__ import annotations
import queue, threading, time

class TrRateLimiter:
    def __init__(self, delay_sec: float = 0.25):
        self.delay_sec=delay_sec
        self.q: queue.Queue = queue.Queue()
        self._stop=False
        self.worker=threading.Thread(target=self._run, daemon=True)
        self.worker.start()

    def submit(self, fn, retries:int=2):
        self.q.put((fn,retries,time.time()))

    def _run(self):
        while not self._stop:
            fn,retries,_=self.q.get()
            try:
                fn()
            except Exception:
                if retries>0:
                    self.q.put((fn,retries-1,time.time()))
            time.sleep(self.delay_sec)

    def stop(self):
        self._stop=True
