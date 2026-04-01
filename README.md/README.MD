# Distributed File Conversion Service

A distributed system where clients upload files to a central server, which distributes conversion jobs across multiple worker nodes.

---

## Project Structure

```
distributed_file_converter/
├── client/
│   └── client.py              # CLI client
├── server/
│   ├── server.py              # Main server (handles clients, dispatches jobs)
│   └── job_queue.py           # Thread-safe job queue
├── workers/
│   ├── worker.py              # Worker node
│   └── converters/
│       ├── image_converter.py # Pillow: jpg↔png, bmp, gif, webp
│       ├── doc_converter.py   # LibreOffice: docx→pdf, txt→pdf
│       └── video_converter.py # ffmpeg: mp4→gif, avi→mp4
├── shared/
│   ├── config.py              # Shared config (host, ports, buffer)
│   └── protocol.py            # send_file / receive_file over TCP
├── analysis/
│   └── performance_plot.py    # File size vs conversion time graph
└── README.md
```

---

## Setup

### Install dependencies
```bash
pip install Pillow matplotlib
sudo apt install libreoffice ffmpeg  # for doc/video conversion
```

---

## How to Run

### Step 1 — Start worker nodes (open 3 terminals)
```bash
python workers/worker.py 0   # listens on port 10000
python workers/worker.py 1   # listens on port 10001
python workers/worker.py 2   # listens on port 10002
```

### Step 2 — Start the server
```bash
python server/server.py
```

### Step 3 — Run the client
```bash
python client/client.py <file_path> <target_format>

# Examples:
python client/client.py photo.jpg png
python client/client.py report.docx pdf
python client/client.py clip.mp4 gif
```

### Step 4 — Run performance analysis (server must be running)
```bash
python analysis/performance_plot.py
```

---

## Supported Conversions

| Type   | Input Formats         | Output Formats        |
|--------|-----------------------|-----------------------|
| Image  | jpg, png, bmp, gif, webp | jpg, png, bmp, gif, webp |
| Doc    | docx, odt, txt, rtf   | pdf                   |
| Video  | mp4, avi, mov, mkv    | mp4, avi, gif, webm   |

---

## Architecture

```
CLIENTS (upload files)
       │ TCP
       ▼
 MAIN SERVER
 ┌─────────────┐
 │  Job Queue  │
 └──────┬──────┘
        │ round-robin
  ┌─────┴─────┐
  ▼           ▼
WORKER 0   WORKER 1  ...
(convert)  (convert)
  │           │
  └─────┬─────┘
        ▼
  result → client
```