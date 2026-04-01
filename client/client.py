import socket
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import HOST, SERVER_PORT
from shared.protocols import send_file, receive_file, send_message, receive_message


def convert_file(filepath, target_format):
    """Connect to server, upload file, and receive converted result."""

    if not os.path.exists(filepath):
        print(f"[CLIENT] File not found: {filepath}")
        return

    print(f"[CLIENT] Connecting to server {HOST}:{SERVER_PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, SERVER_PORT))
        print(f"[CLIENT] Connected!")

        # Step 1: tell server what format we want
        send_message(sock, target_format)

        # Step 2: send the file
        send_file(sock, filepath)
        print(f"[CLIENT] File sent. Waiting for conversion...")

        # Step 3: receive status
        status = receive_message(sock)
        if status.startswith("ERROR"):
            print(f"[CLIENT] Server error: {status}")
            return

        # Step 4: receive converted file
        result_path = receive_file(sock, save_dir=".")
        print(f"[CLIENT] Conversion complete! Saved to: {result_path}")

    except Exception as e:
        print(f"[CLIENT] Error: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    # Usage: python client.py <file_path> <target_format>
    # Example: python client.py photo.jpg png
    if len(sys.argv) != 3:
        print("Usage: python client.py <file_path> <target_format>")
        print("Example: python client.py image.jpg png")
        sys.exit(1)

    file_path = sys.argv[1]
    target_fmt = sys.argv[2].lower()

    convert_file(file_path, target_fmt)