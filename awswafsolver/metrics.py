import random


def generate_precise_value(min_val, max_val):
    precision = random.randint(14, 16)
    value = random.uniform(min_val, max_val)
    return round(value, precision)


def generate_verify_metrics():
    encoding = generate_precise_value(1.5, 2.5)  # SignalEncodingTime
    encryption = generate_precise_value(8.0, 10.0)  # SignalEncryptionTime (Tu rango)
    api_latency = generate_precise_value(140.0, 160.0)  # InputsApiLatency
    cookie_fetch = generate_precise_value(0.4, 0.9)  # CookieFetchTime
    total_time = encoding + encryption + api_latency + cookie_fetch

    return [
        {"name": "2", "unit": "2", "value": encoding},
        {"name": "100", "unit": "2", "value": 0},
        {"name": "101", "unit": "2", "value": 1},
        {"name": "102", "unit": "2", "value": 1},
        {"name": "103", "unit": "2", "value": 18},
        {"name": "104", "unit": "2", "value": 0},
        {"name": "105", "unit": "2", "value": 0},
        {"name": "106", "unit": "2", "value": 0},
        {"name": "107", "unit": "2", "value": 0},
        {"name": "108", "unit": "2", "value": 1},
        {"name": "undefined", "unit": "2", "value": 0},
        {"name": "110", "unit": "2", "value": 0},
        {"name": "111", "unit": "2", "value": 116},
        {"name": "112", "unit": "2", "value": 1},
        {"name": "undefined", "unit": "2", "value": 1},
        {"name": "3", "unit": "2", "value": encryption},
        {"name": "7", "unit": "4", "value": 0},
        {"name": "1", "unit": "2", "value": api_latency},
        {"name": "4", "unit": "2", "value": 6},
        {"name": "5", "unit": "2", "value": cookie_fetch},
        {"name": "6", "unit": "2", "value": total_time},
        {"name": "8", "unit": "4", "value": 1},
    ]


def generate_telemetry_metrics():
    telemetry_encryption = generate_precise_value(0.6, 0.9)
    telemetry_encoding = generate_precise_value(0.2, 0.4)
    return [
        {"name": "12", "unit": "2", "value": telemetry_encoding},
        {"name": "200", "unit": "2", "value": 0},
        {"name": "201", "unit": "2", "value": 1},
        {"name": "13", "unit": "2", "value": telemetry_encryption},
        {"name": "10", "unit": "4", "value": 0},
        {"name": "9", "unit": "4", "value": 0},
        {"name": "11", "unit": "2", "value": 6.5},
    ]
