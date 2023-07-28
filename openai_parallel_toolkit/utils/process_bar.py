import threading

from tqdm import tqdm


class ProgressBar:
    def __init__(self, initial=0, total=0, desc="Progress"):
        self.lock = threading.Lock()
        self.progress_bar = tqdm(total=total, desc=desc, initial=initial, smoothing=0.1)

    def update(self, n=1):
        with self.lock:
            self.progress_bar.update(n)

    def close(self):
        with self.lock:
            self.progress_bar.close()
