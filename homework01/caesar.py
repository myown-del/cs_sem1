def get_pos(ch: str) -> tuple[int, int]:
    if ch.isupper():
        offset = 65
    else:
        offset = 97
    return ord(ch) - offset, offset


def encrypt_caesar(plaintext: str, shift: int = 3) -> str:
    """
    Encrypts plaintext using a Caesar cipher.

    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    ciphertext = ""
    for ch in plaintext:
        if ch.isalpha():
            pos, offset = get_pos(ch)
            ciphertext += chr(((pos + shift) % 26) + offset)
        else:
            ciphertext += ch
    return ciphertext


def decrypt_caesar(ciphertext: str, shift: int = 3) -> str:
    """
    Decrypts a ciphertext using a Caesar cipher.

    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    plaintext = ""
    for ch in ciphertext:
        if ch.isalpha():
            pos, offset = get_pos(ch)
            plaintext += chr(((pos - shift) % 26) + offset)
        else:
            plaintext += ch
    return plaintext

