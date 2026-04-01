import queue
import threading


class Job:
    def __init__(self, job_id, input_path, target_format, client_conn):
        self.job_id = job_id
        self.input_path = input_path
        self.target_format = target_format
        self.client_conn = client_conn  # so server can send result back

    def __repr__(self):
        return f"Job(id={self.job_id}, file={self.input_path}, format={self.target_format})"


class JobQueue:
    def __init__(self):
        self._queue = queue.Queue()
        self._lock = threading.Lock()
        self._counter = 0

    def add_job(self, input_path, target_format, client_conn):
        with self._lock:
            self._counter += 1
            job_id = self._counter

        job = Job(job_id, input_path, target_format, client_conn)
        self._queue.put(job)
        print(f"[QUEUE] Added {job}")
        return job_id

    def get_job(self):
        """Blocks until a job is available."""
        return self._queue.get()

    def task_done(self):
        self._queue.task_done()

    def is_empty(self):
        return self._queue.empty()

    def size(self):
        return self._queue.qsize()