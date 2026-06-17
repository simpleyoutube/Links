import urllib.request
import urllib.error
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_FILE = "links.txt"
TIMEOUT = 10
THREADS = 20

socket.setdefaulttimeout(TIMEOUT)


def test_url(url):
    url = url.strip()

    if not url:
        return None

    # If no scheme, try HTTPS then HTTP
    candidates = []

    if url.startswith(("http://", "https://")):
        candidates.append(url)
    else:
        candidates.append("https://" + url)
        candidates.append("http://" + url)

    for candidate in candidates:
        try:
            req = urllib.request.Request(
                candidate,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                return (
                    url,
                    candidate,
                    response.status,
                    response.geturl()
                )

        except Exception:
            pass

    return (url, None, "FAILED", None)


def main():
    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        links = [line.strip() for line in f if line.strip()]

    working = []
    failed = []

    print(f"Testing {len(links)} links...\n")

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = [executor.submit(test_url, link) for link in links]

        for future in as_completed(futures):
            result = future.result()

            if result is None:
                continue

            original, tested, status, final_url = result

            if tested:
                print(f"[OK] {tested} -> {status}")
                working.append(final_url or tested)
            else:
                print(f"[FAIL] {original}")
                failed.append(original)

    with open("working_links.txt", "w", encoding="utf-8") as f:
        for link in sorted(set(working)):
            f.write(link + "\n")

    with open("failed_links.txt", "w", encoding="utf-8") as f:
        for link in sorted(set(failed)):
            f.write(link + "\n")

    print("\nDone.")
    print(f"Working: {len(working)}")
    print(f"Failed: {len(failed)}")
    print("Saved to working_links.txt and failed_links.txt")


if __name__ == "__main__":
    main()
