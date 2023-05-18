import threading

from tqdm import tqdm


class ProgressBar:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, total=0, desc="Progress"):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    obj = super(ProgressBar, cls).__new__(cls)
                    obj.progress_bar = tqdm(total=total, desc=desc)
                    cls._instance = obj
        return cls._instance

    def update(self, n=1):
        with self._lock:
            self.progress_bar.update(n)

    def close(self):
        with self._lock:
            self.progress_bar.close()

    @classmethod
    def destroy(cls):
        with cls._lock:
            cls._instance = None
