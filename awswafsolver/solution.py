import base64
import hashlib
import json
import math


def retrieve_dict_from_jwttoken(challenge_token: str) -> dict:
    decoded_bytes = base64.b64decode(challenge_token)
    decoded_str = decoded_bytes.decode("utf-8")
    return json.loads(decoded_str)


def verify_bit_prefix(difficulty, hash_result):
    chars_to_review = math.ceil(difficulty / 4)
    binary_string = "".join(f"{int(c, 16):04b}" for c in hash_result[:chars_to_review])
    return binary_string[:difficulty] == "0" * difficulty


def solve_aws_challenge_sha2(
    challenge_token: str, checksum: str, difficulty: str
) -> str:
    nonce = 0
    while True:
        candidate = f"{challenge_token}{checksum}{nonce}"
        hash_result = hashlib.sha256(candidate.encode("utf-8")).hexdigest()

        if verify_bit_prefix(difficulty, hash_result):
            return str(nonce)

        nonce += 1
        if nonce % 1000000 == 0:
            raise ValueError(f"No nonce found after {nonce} tries")


def solve_challenge(challenge_token: str, checksum: str) -> dict:
    jwt_dict = retrieve_dict_from_jwttoken(challenge_token)

    challenge_map = {
        "HashcashScrypt": solve_aws_challenge_scrypt,
        "HashcashSHA2": solve_aws_challenge_sha2,
    }

    challenge_type = jwt_dict.get("challenge_type")

    method = challenge_map.get(challenge_type)

    if not method:
        raise ValueError(f"Tipo de challenge no soportado: {challenge_type}")
    difficulty = jwt_dict.get("difficulty")
    return method(challenge_token, checksum, difficulty)


def solve_aws_challenge_scrypt(
    challenge_token: str, checksum: str, difficulty: str
) -> str:
    N = 128
    R = 8
    P = 1
    DKLEN = 16

    nonce = 0
    while True:
        candidate = f"{challenge_token}{checksum}{nonce}"
        hash_result = hashlib.scrypt(
            password=candidate.encode("utf-8"),
            salt=checksum.encode("utf-8"),
            n=N,
            r=R,
            p=P,
            maxmem=2000000,
            dklen=DKLEN,
        )
        hash_hex = hash_result.hex()
        binary_start = bin(int(hash_hex[:difficulty], 16))[2:].zfill(difficulty * 4)

        if binary_start.startswith("0" * difficulty):
            return str(nonce)

        nonce += 1
        if nonce % 1000 == 0:
            raise ValueError(f"No nonce found after {nonce} tries")
