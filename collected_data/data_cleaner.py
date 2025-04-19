import os
import re
from collections import defaultdict

def extract_metrics(line):
    """Extracts throughput and latency values from a line."""
    throughput_match = re.search(r'\[THROUGHPUT\] ([\d.]+) bytes/sec', line)
    latency_match = re.search(r'\[LATENCY\] ([\d.]+) sec/packet', line)
    if throughput_match and latency_match:
        return float(throughput_match.group(1)), float(latency_match.group(1))
    return None, None

def extract_byte_size(line):
    """Extracts the byte size from a line like: [128 bytes]"""
    match = re.search(r'\[(\d+) bytes\]', line)
    return int(match.group(1)) if match else None

def process_logs(directory='logs'):
    byte_groups = defaultdict(list)

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)

            with open(filepath, 'r') as file:
                lines = file.readlines()

            for i in range(1, len(lines)):
                if '[THROUGHPUT]' in lines[i]:
                    byte_size = extract_byte_size(lines[i - 1])
                    throughput, latency = extract_metrics(lines[i])
                    if byte_size is not None and throughput is not None and latency is not None:
                        byte_groups[byte_size].append((throughput, latency))

    # Calculate averages and track max/min
    highest_throughput = float('-inf')
    lowest_latency = float('inf')

    for byte_size, metrics in byte_groups.items():
        avg_throughput = sum(m[0] for m in metrics) / len(metrics)
        avg_latency = sum(m[1] for m in metrics) / len(metrics)
        print(f"[{byte_size} bytes] → Avg Throughput: {avg_throughput:.2f} bytes/sec | Avg Latency: {avg_latency:.4f} sec/packet")

        highest_throughput = max(highest_throughput, *[m[0] for m in metrics])
        lowest_latency = min(lowest_latency, *[m[1] for m in metrics])

    print("\n🔺 Highest Throughput:", f"{highest_throughput:.2f} bytes/sec")
    print("🔻 Lowest Latency:", f"{lowest_latency:.4f} sec/packet")

# Run the processing
process_logs()
