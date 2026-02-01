from .constants import ALPHABET, CRC_TABLE


def utf8_encoder_encode(text):
    result = []
    for char in text:
        char_code = ord(char)
        if char_code < 0x80:
            result.append(chr(char_code))
        elif char_code < 0x800:
            result.append(chr((char_code >> 6) | 0xC0))
            result.append(chr((char_code & 0x3F) | 0x80))
        else:
            result.append(chr((char_code >> 12) | 0xE0))
            result.append(chr(((char_code >> 6) & 0x3F) | 0x80))
            result.append(chr((char_code & 0x3F) | 0x80))

    return "".join(result)


def crc32_calculate(data):
    MASK = 0xFFFFFFFF
    crc = MASK

    for i in range(len(data)):
        char_code = ord(data[i])
        index = (crc ^ char_code) & 0xFF
        crc = ((crc >> 8) & 0x00FFFFFF) ^ (CRC_TABLE[index] & MASK)
    return (crc ^ MASK) & MASK


def get_check_sum(crc_value):
    res = ""
    for i in range(7, -1, -1):
        idx = (crc_value >> (i * 4)) & 0xF
        res += ALPHABET[idx]
    return res
