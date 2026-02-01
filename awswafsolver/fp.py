import json
import random
import time
import uuid


def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def adjust_fp(chrome_version: str) -> dict:
    fp_template = read_json("./awswafsolver/fp.json")
    now_timestamp = int(time.time() * 1000)
    duration = random.randint(1, 10)
    fp_template["start"] = now_timestamp
    fp_template["end"] = now_timestamp + duration
    fp_template["userAgent"] = (
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}.0.0.0 Safari/537.36"  # TODO constants chrome version
    )
    fp_template["id"] = str(uuid.uuid4())
    return fp_template
