import matplotlib.pyplot as plt
import time
import socket
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import HOST, SERVER_PORT
from shared.protocols import send_file, receive_file, send_message, receive_message


def generate_test_image(size_kb, path):
    """Generate a test image of approximately size_kb kilobytes."""
    from PIL import Image
    import random

    # Approximate: each pixel = 3 bytes (RGB)
    pixels_needed = (size_kb * 1024) // 3
    width = int(pixels_needed ** 0.5)
    height = width

    img = Image.new('RGB', (width, height))
    pixels = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
              for _ in range(width * height)]
    img.putdata(pixels)
    img.save(path, 'JPEG')
    actual_size = os.path.getsize(path) / 1024
    print(f"[ANALYSIS] Generated test image: {path} (~{actual_size:.1f} KB)")
    return path


def measure_conversion_time(filepath, target_format):
    """Send file to server and measure round-trip conversion time."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, SERVER_PORT))
        send_message(sock, target_format)

        start = time.time()
        send_file(sock, filepath)

        status = receive_message(sock)
        if status.startswith("ERROR"):
            print(f"[ANALYSIS] Server error: {status}")
            return None

        receive_file(sock, save_dir="analysis_outputs")
        elapsed = time.time() - start

        return elapsed
    except Exception as e:
        print(f"[ANALYSIS] Error: {e}")
        return None
    finally:
        sock.close()


def run_analysis():
    """Run conversions across different file sizes and plot results."""
    os.makedirs("test_files", exist_ok=True)
    os.makedirs("analysis_outputs", exist_ok=True)

    # File sizes to test (in KB)
    sizes_kb = [50, 100, 200, 500, 1000, 2000]
    times = []

    print("[ANALYSIS] Starting performance analysis...")

    for size in sizes_kb:
        test_path = f"test_files/test_{size}kb.jpg"
        generate_test_image(size, test_path)

        print(f"[ANALYSIS] Testing {size} KB file...")
        elapsed = measure_conversion_time(test_path, "png")

        if elapsed is not None:
            times.append(elapsed)
            print(f"[ANALYSIS] {size} KB → {elapsed:.3f} seconds")
        else:
            times.append(0)

    # Plot results
    plt.figure(figsize=(10, 6))
    plt.plot(sizes_kb, times, marker='o', color='steelblue', linewidth=2, markersize=8)
    plt.fill_between(sizes_kb, times, alpha=0.15, color='steelblue')

    plt.title("Distributed File Conversion: File Size vs Conversion Time", fontsize=14, fontweight='bold')
    plt.xlabel("File Size (KB)", fontsize=12)
    plt.ylabel("Conversion Time (seconds)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(sizes_kb)

    # Annotate each point
    for x, y in zip(sizes_kb, times):
        plt.annotate(f"{y:.2f}s", (x, y), textcoords="offset points",
                     xytext=(0, 10), ha='center', fontsize=9)
    plt.xscale('log')  # spreads out the x-axis nicely
    
    plt.tight_layout()
    plot_path = "analysis/performance_result.png"
    plt.savefig(plot_path, dpi=150)
    print(f"[ANALYSIS] Plot saved to {plot_path}")
    plt.show()


if __name__ == "__main__":
    run_analysis()