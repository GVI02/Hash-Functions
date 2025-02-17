from numpy import uint32


def print_words(list_of_words: list[uint32]):
    """Helper function to print a list of 32-bit words"""
    print(" ".join([f"{word:08X}" for word in list_of_words]))


def congruent(a: int, b: int, m: int) -> bool:
    """Return whether a and b are congruent modulo m"""
    diff = a - b
    return diff % m == 0


def blocks(words: list) -> list:
    """Helper function to split list of 32-bit words into blocks of 16. Each chunk has 512 bits"""
    for i in range(0, len(words), 16):
        yield words[i:i + 16]


def rotl(x: uint32, n: int):
    """"Circular shift (rotate) the first @n bits from @x to the left.\n
    Ex.: leftrotate(0b101000, 3) -> 0b000101"""
    return uint32((x << n) | (x >> 32 - n))
