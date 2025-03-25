import subprocess

def ping_host(host="8.8.8.8", count=1, timeout=1, max_output_len=64):
    """Ping a host and return the output (truncated to fit LoRa limits)."""
    try:
        result = subprocess.run(
            ["ping", "-c", str(count), "-W", str(timeout), host],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        output = result.stdout.strip()
    except Exception as e:
        output = f"[PING ERROR] {e}"
    return output[:max_output_len]


def check_dns(domain="google.com", max_output_len=64):
    """Do a basic DNS lookup test."""
    try:
        result = subprocess.run(
            ["nslookup", domain],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        output = result.stdout.strip()
    except Exception as e:
        output = f"[DNS ERROR] {e}"
    return output[:max_output_len]


def check_internet_connectivity(max_output_len=64):
    """Check if we can reach a known URL using curl (or similar)."""
    try:
        result = subprocess.run(
            ["curl", "-Is", "https://github.com", "--max-time", "3"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        output = result.stdout.strip()
    except Exception as e:
        output = f"[CONNECTIVITY ERROR] {e}"
    return output[:max_output_len]
