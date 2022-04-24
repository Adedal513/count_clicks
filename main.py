import argparse
import os


from urllib.parse import urlparse

import dotenv

from dotenv import load_dotenv

import requests

from requests import exceptions
from requests import get
from requests import post


load_dotenv()
token = os.environ["BITLY_TOKEN"]
request_header = {"Authorization": f"Bearer {token}"}
API_URL = "https://api-ssl.bitly.com/v4/"


def shorten_link(auth_header: dict, url: str) -> str:
    get_shorten_link_url = f"{API_URL}shorten"
    payload = {
        "long_url": url,
    }

    response = post(url=get_shorten_link_url, headers=auth_header, json=payload)
    response.raise_for_status()

    shorten_link = response.json()["id"]

    return shorten_link


def count_clicks(auth_header: dict, bitlink: str) -> int:
    get_clicks_url = f"{API_URL}bitlinks/{bitlink}/clicks/summary"

    response = get(url=get_clicks_url, headers=auth_header)
    response.raise_for_status()

    clicks = response.json()["total_clicks"]

    return clicks


def check_url_accessibility(url: str):
    response = get(url=url)
    response.raise_for_status()


def is_bitlink(url: str, auth_header: dict) -> bool:
    request_url = f"{API_URL}bitlinks/{url}"
    response = get(url=request_url, headers=auth_header)

    return response.ok


def strip_url(url: str) -> str:
    parsed_url = urlparse(url)
    trimmed_url = parsed_url.netloc + parsed_url.path

    return trimmed_url


def main():

    parser = argparse.ArgumentParser(
        description="Сокращение ссылок при помощи сервиса Bitly и вывод сатистики по кликам"
    )
    parser.add_argument("URL", help="Ссылка (сокращенная или полная)")
    args = parser.parse_args()

    input_url = args.URL

    url_without_protocol = strip_url(input_url)

    try:
        check_url_accessibility(url=input_url)

        if is_bitlink(url_without_protocol, request_header):
            clicks = count_clicks(
                auth_header=request_header, bitlink=url_without_protocol
            )
            print(f"Всего кликов на ссылку {url_without_protocol}: {clicks}")
        else:
            short_url = shorten_link(auth_header=request_header, url=input_url)
            print(f"Короткая ссылка: {short_url}")
    except exceptions.HTTPError:
        print("Ссылка некорректна, попробуйте снова.")


if __name__ == "__main__":
    main()
