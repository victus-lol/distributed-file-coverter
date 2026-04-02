import socket
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.config import HOST, SERVER_PORT, MAX_CLIENTS, NUM_WORKERS, WORKER_BASE_PORT, UPLOAD_DIR
from shared.protocols import receive_file, send_file, send_message, receive_message
from job_queue import JobQueue

job_queue = JobQueue()

worker_index = 0
worker_lock = threading.Lock()

def get_next_worker_port():
    global worker_index
    with worker_lock:
        port = WORKER_BASE_PORT + (worker_index % NUM_WORKERS)
        worker_index += 1
    return port

def dispatch_to_worker(job):
    worker_port = get_next_worker_port()
    print(f"[SERVER] Dispatching Job {job.job_id} to worker on port {worker_port}")
    try:
        worker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        worker_sock.connect((HOST, worker_port))
        send_message(worker_sock, job.target_format)
        send_file(worker_sock, job.input_path)
        result_path = receive_file(worker_sock, save_dir="outputs")
        worker_sock.close()
        return result_path
    except Exception as e:
        print(f"[SERVER] Worker error on port {worker_port}: {e}")
        return None

def handle_client(conn, addr):
    print(f"[SERVER] New client connected: {addr}")
    try:
        target_format = receive_message(conn)
        print(f"[SERVER] Client {addr} wants format: {target_format}")

        saved_path = receive_file(conn, save_dir=UPLOAD_DIR)

        job = job_queue.add_job(saved_path, target_format, conn)  # ← now a Job object
        result_path = dispatch_to_worker(job)                      # ← no broken get_job()
        job_queue.task_done()                                      # ← was never called

        if result_path and os.path.exists(result_path):
            send_message(conn, "SUCCESS")
            send_file(conn, result_path)
        else:
            send_message(conn, "ERROR: Conversion failed")
    except Exception as e:
        print(f"[SERVER] Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"[SERVER] Connection closed: {addr}")

def start_server():
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, SERVER_PORT))
    server.listen(MAX_CLIENTS)
    print(f"[SERVER] Started on {HOST}:{SERVER_PORT} | Max clients: {MAX_CLIENTS}")
    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
            print(f"[SERVER] Active threads: {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
