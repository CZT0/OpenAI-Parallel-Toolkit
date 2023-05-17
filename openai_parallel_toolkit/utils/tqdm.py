import threading

from tqdm import tqdm


class ProgressBar:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, total=0, desc="Progress"):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ProgressBar, cls).__new__(cls)
                    cls._instance.progress_bar = tqdm(total=total, desc=desc)
        return cls._instance

    def update(self, n=1):
        with self._lock:
            self.progress_bar.update(n)

    def close(self):
        with self._lock:
            self.progress_bar.close()
