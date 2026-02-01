import json
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from curl_cffi import requests

from .checksum import crc32_calculate, get_check_sum, utf8_encoder_encode
from .fp import adjust_fp
from .metrics import generate_verify_metrics
from .signals import encrypt_zoey, prepare_signals
from .solution import solve_challenge


class AWSWAFSolver:
    def __init__(self, target_url: str, chrome_version: str):
        self.session = requests.Session()
        self.chrome_version = chrome_version
        self.target_url = target_url
        parsed = urlparse(target_url)
        self.base_url = f"{parsed.scheme}://{parsed.netloc}"

    def general_request(self, url: str) -> requests.Response:
        headers = {
            "Ect": "4g",
            "Sec-Ch-Ua": f'"Not(A:Brand";v="8", "Chromium";v="{self.chrome_version}"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Accept-Language": "es-ES,es;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.chrome_version}.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": self.target_url,
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=0, i",
            "Connection": "keep-alive",
        }
        response = self.session.get(
            url,
            headers=headers,
            impersonate=f"chrome{self.chrome_version}",
        )
        return response

    def parse_challenge_url(self, soup: BeautifulSoup):
        challenge_script = soup.find("script", src=lambda x: x and "challenge.js" in x)

        if challenge_script:
            challenge_url = challenge_script["src"]
            return challenge_url
        return ""

    def verify_request(
        self,
        verify_url: str,
        challenge: dict,
        checksum: str,
        metrics: list,
        signals: list,
        solution: str,
    ):
        headers = {
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Ect": "4g",
            "Accept-Language": "es-ES,es;q=0.9",
            "Sec-Ch-Ua": f'"Not(A:Brand";v="8", "Chromium";v="{self.chrome_version}"',
            "Content-Type": "text/plain;charset=UTF-8",
            "Sec-Ch-Ua-Mobile": "?0",
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{self.chrome_version}.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Origin": self.base_url,
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": self.target_url,
            "Accept-Encoding": "gzip, deflate, br",
            "Priority": "u=1, i",
        }

        payload = {
            "challenge": challenge,
            "checksum": checksum,
            "client": "Browser",
            "domain": "booking.com",
            "existing_token": None,
            "metrics": metrics,
            "signals": signals,
            "solution": solution,
        }
        return self.session.post(
            verify_url,
            headers=headers,
            json=payload,
            impersonate=f"chrome{self.chrome_version}",
        )

    def retrieve_session(self) -> requests.Session:
        first_response = self.general_request(self.base_url)
        soup = BeautifulSoup(first_response.text, "html.parser")
        challenge_url = self.parse_challenge_url(soup)
        self.general_request(challenge_url)
        challenge_request_url = challenge_url.replace(
            "challenge.js", "inputs?client=browser"
        )
        challenge_response = self.general_request(challenge_request_url)
        challenge_rjson = challenge_response.json()
        challenge = challenge_rjson.get("challenge", {})
        challenge_token = challenge.get("input")
        verify_url = challenge_url.replace("challenge.js", "verify")
        verify_fp = adjust_fp(self.chrome_version)
        verify_json_str = json.dumps(
            verify_fp, separators=(",", ":"), ensure_ascii=False
        )
        verify_encoded_json_str = utf8_encoder_encode(verify_json_str)
        verify_crc = crc32_calculate(verify_encoded_json_str)
        verify_checksum = get_check_sum(verify_crc)
        verify_checksum_fp = f"{verify_checksum}#{verify_json_str}"
        verify_zoey_str = encrypt_zoey(verify_checksum_fp)
        verify_signals = prepare_signals(verify_zoey_str)
        solution = solve_challenge(challenge_token, verify_checksum)
        verify_metrics = generate_verify_metrics()
        verify_response = self.verify_request(
            verify_url,
            challenge,
            verify_checksum,
            verify_metrics,
            verify_signals,
            solution,
        )
        verify_rjson = verify_response.json()
        verify_token = verify_rjson.get("token")
        self.session.cookies.set("aws-waf-token", verify_token)
        return self.session
