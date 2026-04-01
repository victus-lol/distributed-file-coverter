import socket
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import HOST, WORKER_BASE_PORT, BUFFER_SIZE
from shared.protocols import receive_file, send_file, receive_message
from workers.converters import image_converter, doc_converter, video_converter


WORK_DIR = "worker_temp"


def pick_converter(input_path, target_format):
    """Select the right converter based on file type."""
    if image_converter.can_handle(input_path, target_format):
        return image_converter
    elif video_converter.can_handle(input_path, target_format):
        return video_converter
    elif doc_converter.can_handle(input_path, target_format):
        return doc_converter
    else:
        return None


def handle_job(conn):
    """Receive a job from the server, convert the file, send result back."""
    os.makedirs(WORK_DIR, exist_ok=True)

    try:
        # Step 1: receive target format
        target_format = receive_message(conn)
        print(f"[WORKER] Target format: {target_format}")

        # Step 2: receive file
        input_path = receive_file(conn, save_dir=WORK_DIR)
        print(f"[WORKER] Received file: {input_path}")

        # Step 3: convert
        converter = pick_converter(input_path, target_format)
        if converter is None:
            raise ValueError(f"No converter for {input_path} → {target_format}")

        output_path = converter.convert(input_path, target_format)

        # Step 4: send result back
        send_file(conn, output_path)
        print(f"[WORKER] Job done. Sent: {output_path}")

        # Cleanup temp files
        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        print(f"[WORKER] Error: {e}")
    finally:
        conn.close()


def start_worker(worker_id=0):
    port = WORKER_BASE_PORT + worker_id
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, port))
    server.listen(5)
    print(f"[WORKER {worker_id}] Listening on {HOST}:{port}")

    try:
        while True:
            conn, addr = server.accept()
            print(f"[WORKER {worker_id}] Job received from {addr}")
            handle_job(conn)
    except KeyboardInterrupt:
        print(f"\n[WORKER {worker_id}] Shutting down.")
    finally:
        server.close()


if __name__ == "__main__":
    # Usage: python worker.py <worker_id>
    # Example: python worker.py 0   → listens on port 10000
    #          python worker.py 1   → listens on port 10001
    worker_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    start_worker(worker_id)