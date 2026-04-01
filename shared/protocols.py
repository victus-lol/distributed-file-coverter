import socket
import os


def send_file(sock, filepath):
    """Send a file over a socket with a header containing filename and size."""
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    # Header: [name_len (10 bytes)] [filename] [filesize (20 bytes)]
    sock.send(f"{len(filename):<10}".encode())
    sock.send(filename.encode())
    sock.send(f"{filesize:<20}".encode())

    with open(filepath, 'rb') as f:
        while chunk := f.read(4096):
            sock.send(chunk)

    print(f"[PROTOCOL] Sent: {filename} ({filesize} bytes)")


def receive_file(sock, save_dir="."):
    """Receive a file from a socket and save it to save_dir."""
    os.makedirs(save_dir, exist_ok=True)

    name_len = int(sock.recv(10).decode().strip())
    filename = sock.recv(name_len).decode()
    filesize = int(sock.recv(20).decode().strip())

    save_path = os.path.join(save_dir, filename)
    received = 0

    with open(save_path, 'wb') as f:
        while received < filesize:
            chunk = sock.recv(min(4096, filesize - received))
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)

    print(f"[PROTOCOL] Received: {filename} ({received} bytes) → {save_path}")
    return save_path


def send_message(sock, message):
    """Send a short string message (max 1024 bytes)."""
    msg = message.encode().ljust(1024)
    sock.send(msg)


def receive_message(sock):
    """Receive a short string message."""
    return sock.recv(1024).decode().strip()