import argparse
import http.client
from time import perf_counter
from urllib.parse import urlsplit
from urllib.request import urlopen


REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024
TIMEOUT_SECONDS = 30


def download(url: str) -> tuple[int, float]:
    downloaded_bytes = 0
    started_at = perf_counter()
    with urlopen(url, timeout=TIMEOUT_SECONDS) as response:
        while chunk := response.read(CHUNK_SIZE):
            downloaded_bytes += len(chunk)

        content_length = response.headers.get("Content-Length")
        if content_length and "Transfer-Encoding" not in response.headers:
            expected_bytes = int(content_length)
            if downloaded_bytes != expected_bytes:
                raise OSError(
                    f"неполный ответ: получено {downloaded_bytes} из {expected_bytes} байт"
                )

    return downloaded_bytes, perf_counter() - started_at


def main() -> None:
    parser = argparse.ArgumentParser(description="Измерение скорости скачивания по URL")
    parser.add_argument("url", metavar="URL", help="адрес файла (http:// или https://)")
    args = parser.parse_args()

    try:
        url = urlsplit(args.url)
    except ValueError as error:
        parser.error(str(error))
    if url.scheme not in ("http", "https") or not url.hostname:
        parser.error("укажите полный URL с http:// или https://")

    total_bytes = 0
    total_seconds = 0.0
    for request_number in range(1, REQUEST_COUNT + 1):
        try:
            downloaded_bytes, elapsed_seconds = download(args.url)
        except (OSError, http.client.HTTPException, ValueError) as error:
            parser.exit(1, f"Запрос {request_number}/{REQUEST_COUNT}: {error}\n")
        total_bytes += downloaded_bytes
        total_seconds += elapsed_seconds

    average_seconds = total_seconds / REQUEST_COUNT
    speed_mbps = total_bytes * 8 / total_seconds / 1_000_000
    print(f"Среднее время запроса: {average_seconds:.3f} с")
    print(f"Скачано всего: {total_bytes} байт")
    print(f"Скорость скачивания: {speed_mbps:.3f} Мбит/с")


if __name__ == "__main__":
    main()
