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
    challenge_token: str,
    checksum: str,
) -> str:
    # h7b0c470f0cfe3a80a9e26526ad185f484f6817d0832712a4a37a908786a6a67f
    nonce = 0
    jwt_dict = retrieve_dict_from_jwttoken(challenge_token)
    difficulty = jwt_dict.get("difficulty")
    while True:
        candidate = f"{challenge_token}{checksum}{nonce}"
        hash_result = hashlib.sha256(candidate.encode("utf-8")).hexdigest()

        if verify_bit_prefix(difficulty, hash_result):
            return str(nonce)

        nonce += 1
        if nonce % 1000000 == 0:
            raise ValueError(f"No nonce found after {nonce} tries")


def solve_aws_challenge_scrypt(challenge_token: str, checksum: str) -> str:
    # h72f957df656e80ba55f5d8ce2e8c7ccb59687dba3bfb273d54b08a261b2f3002
    jwt_dict = retrieve_dict_from_jwttoken(challenge_token)
    difficulty = jwt_dict.get("difficulty")
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


def solve_aws_challenge_networkbandwidth(
    challenge_token: str,
    checksum: str,
):
    jwt_dict = retrieve_dict_from_jwttoken(challenge_token)
    difficulty = jwt_dict.get("difficulty")
    difficulty_map = {1: 1024, 2: 10240, 3: 102400, 4: 1048576, 5: 10485760}
    size = difficulty_map.get(difficulty)
    buffer = bytes(size)
    base64_content = base64.b64encode(buffer).decode("utf-8")

    return base64_content


def solve_challenge(challenge_token: str, checksum: str) -> dict:
    jwt_dict = retrieve_dict_from_jwttoken(challenge_token)

    challenge_map = {
        "HashcashScrypt": solve_aws_challenge_scrypt,
        "HashcashSHA2": solve_aws_challenge_sha2,
        "NetworkBandwidth": solve_aws_challenge_networkbandwidth,
    }

    challenge_type = jwt_dict.get("challenge_type")

    method = challenge_map.get(challenge_type)

    if not method:
        raise ValueError(f"Unsuported challenge_type: {challenge_type}")
    return method(challenge_token, checksum)
