import argparse
import re
from http.client import HTTPException
from time import perf_counter
from urllib.request import urlopen


REQUEST_COUNT = 10


def main() -> None:
    parser = argparse.ArgumentParser(description="Измерение скорости скачивания по URL")
    parser.add_argument("url", metavar="URL", help="адрес файла, по умолчанию HTTPS")
    url = parser.parse_args().url.strip()
    if not url:
        parser.error("укажите адрес файла")
    protocol = re.match(r"^([a-z][a-z0-9+.-]*)://", url, re.IGNORECASE)
    if protocol is None:
        url = f"https://{url.removeprefix('//')}"
    elif protocol.group(1).lower() not in ("http", "https"):
        parser.error("поддерживаются только HTTP и HTTPS")

    total_bytes = 0
    total_seconds = 0.0
    for request_number in range(1, REQUEST_COUNT + 1):
        request_bytes = 0
        started_at = perf_counter()
        try:
            with urlopen(url, timeout=30) as response:
                while chunk := response.read(64 * 1024):
                    request_bytes += len(chunk)

                if "Transfer-Encoding" not in response.headers:
                    content_length = response.getheader("Content-Length")
                    if content_length is not None and request_bytes != int(content_length):
                        raise OSError("ответ оборвался до получения всех данных")
        except (OSError, HTTPException, ValueError) as error:
            parser.exit(1, f"Запрос {request_number}/{REQUEST_COUNT}: {error}\n")
        total_bytes += request_bytes
        total_seconds += perf_counter() - started_at

    average_seconds = total_seconds / REQUEST_COUNT
    speed_mbps = total_bytes * 8 / total_seconds / 1_000_000
    print(f"Среднее время запроса: {average_seconds:.3f} с")
    print(f"Скачано всего: {total_bytes} байт")
    print(f"Скорость скачивания: {speed_mbps:.3f} Мбит/с")


if __name__ == "__main__":
    main()
