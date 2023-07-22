def get_pos(ch: str) -> tuple[int, int]:
    if ch.isupper():
        offset = 65
    else:
        offset = 97
    return ord(ch) - offset, offset


def encrypt_vigenere(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using a Vigenere cipher.

    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    ciphertext = ""
    for i, ch in enumerate(plaintext):
        encrypt_ch = keyword[i % len(keyword)]
        encrypt_pos, _ = get_pos(encrypt_ch)
        if ch.isalpha():
            pos, offset = get_pos(ch)
            ciphertext += chr(((pos + encrypt_pos) % 26) + offset)
        else:
            ciphertext += ch
    return ciphertext


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    """
    Decrypts a ciphertext using a Vigenere cipher.

    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    plaintext = ""
    for i, ch in enumerate(ciphertext):
        encrypt_ch = keyword[i % len(keyword)]
        encrypt_pos, _ = get_pos(encrypt_ch)
        if ch.isalpha():
            pos, offset = get_pos(ch)
            plaintext += chr(((pos - encrypt_pos) % 26) + offset)
        else:
            plaintext += ch
    return plaintext
