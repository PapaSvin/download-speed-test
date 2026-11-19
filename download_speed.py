import argparse
import re
from http.client import HTTPException
from time import perf_counter
from urllib.request import urlopen


def main() -> None:
    parser = argparse.ArgumentParser(description="Измерение скорости скачивания по URL")
    parser.add_argument("url", metavar="URL", help="адрес файла, по умолчанию HTTPS")
    url = parser.parse_args().url.strip()
    protocol = re.match(r"^([a-z][a-z0-9+.-]*)://", url, re.IGNORECASE)
    if not url or (protocol and protocol.group(1).lower() not in ("http", "https")):
        parser.error("укажите HTTP(S)-адрес файла")
    if protocol is None:
        url = f"https://{url.removeprefix('//')}"

    request_count = 10
    total_bytes = 0
    started_at = perf_counter()
    try:
        for request_number in range(1, request_count + 1):
            with urlopen(url, timeout=30) as response:
                request_bytes = 0
                while chunk := response.read(64 * 1024):
                    request_bytes += len(chunk)

                if "Transfer-Encoding" not in response.headers:
                    content_length = response.getheader("Content-Length")
                    if content_length is not None and request_bytes != int(content_length):
                        raise OSError("ответ оборвался до получения всех данных")
            total_bytes += request_bytes
    except (OSError, HTTPException, ValueError) as error:
        parser.exit(1, f"Запрос {request_number}/{request_count}: {error}\n")

    total_seconds = perf_counter() - started_at
    speed_mbps = total_bytes * 8 / total_seconds / 1000000
    print(f"Среднее время запроса: {total_seconds / request_count:.3f} с")
    print(f"Скачано всего: {total_bytes} байт")
    print(f"Скорость скачивания: {speed_mbps:.3f} Мбит/с")


if __name__ == "__main__":
    main()
