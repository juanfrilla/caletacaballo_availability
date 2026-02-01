import base64
import binascii
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .constants import HEXKEY


def generate_noise():
    """Genera 12 bytes aleatorios (IV)"""
    return os.urandom(12)


def hex_to_bytes(hex_string):
    """Equivalente a hexToUint8Array"""
    if len(hex_string) % 2 != 0:
        hex_string = "0" + hex_string
    return binascii.unhexlify(hex_string)


def bytes_to_hex(data):
    """Equivalente a bufToHex"""
    return binascii.hexlify(data).decode("utf-8")


def encode64(data):
    """Equivalente a encode64 (btoa)"""
    return base64.b64encode(data).decode("utf-8")


def encrypt_zoey(checksum_fp):
    """
    Función principal que genera el token Zoey.
    Equivalente a la función encrypt() de JS.
    """
    key_bytes = hex_to_bytes(HEXKEY)
    iv = generate_noise()
    aesgcm = AESGCM(key_bytes)
    data_bytes = checksum_fp.encode("utf-8")
    encrypted_raw = aesgcm.encrypt(iv, data_bytes, None)
    tag_length = 16
    ciphertext_bytes = encrypted_raw[:-tag_length]
    tag_bytes = encrypted_raw[-tag_length:]
    noise_64 = encode64(iv)
    tag_hex = bytes_to_hex(tag_bytes)
    output_hex = bytes_to_hex(ciphertext_bytes)
    return f"Zoey::{noise_64}::{tag_hex}::{output_hex}"


def add_status_to_payload(payload):
    """
    Normaliza el estado basado en si el payload existe o es nulo.
    """
    current_status = "Present"

    if not payload:
        current_status = "Error"

    return {"status": current_status, "value": payload}


def wrap_as_zoey_object(data_object):
    """
    Empaqueta el valor según el estado del objeto.
    """
    status = data_object.get("status")
    value = data_object.get("value")

    if status == "Present":
        return {"Present": value}

    if status == "Error":
        return {"Error": ""}
    raise ValueError(f"Invalid status: {status}")


def prepare_signals(raw_telemetry_string):
    """
    Función principal que procesa el string 'Zoey::Base64::Tag::Cipher'.
    """
    try:
        first_separator_pos = raw_telemetry_string.index("::")
    except ValueError:
        raise ValueError("Invalid string telemetry format (Missing '::')")
    engine_id = raw_telemetry_string[:first_separator_pos]
    data_block = raw_telemetry_string[first_separator_pos + 2 :]
    status_payload = add_status_to_payload(data_block)
    processed_value = wrap_as_zoey_object(status_payload)
    return [
        {
            "name": engine_id,
            "value": processed_value,
        }
    ]
