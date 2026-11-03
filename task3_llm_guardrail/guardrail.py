import re

REDACTION = "[REDACTED]"

# Email: limit local part to 64 characters.
EMAIL_PATTERN = re.compile(
    r"(?<![\w.+-])[A-Z0-9.!#$%&'*+/=?^_`{|}~-]{1,64}"
    r"@[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?"
    r"(?:\.[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?)+",
    re.IGNORECASE,
)

SSN_PATTERN = re.compile(r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)")

CARD_PATTERN = re.compile(
    r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)"
)

# Valid email addresses are bounded; retain more than their maximum length.
BUFFER_SIZE = 512


def passes_luhn(number: str) -> bool:
    digits = [int(char) for char in number if char.isdigit()]

    if not 13 <= len(digits) <= 19:
        return False

    checksum = 0
    reversed_digits = digits[::-1]

    for index, digit in enumerate(reversed_digits):
        if index % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit

    return checksum % 10 == 0


class PIIRedactor:
    def __init__(self):
        self.buffer = ""

    def redact(self, text: str) -> str:
        text = EMAIL_PATTERN.sub(REDACTION, text)
        text = SSN_PATTERN.sub(REDACTION, text)

        def replace_card(match):
            candidate = match.group()
            if passes_luhn(candidate):
                return REDACTION
            return candidate

        return CARD_PATTERN.sub(replace_card, text)

    def feed(self, chunk: str, final: bool = False) -> str:
        self.buffer += chunk

        if final:
            safe_text = self.buffer
            self.buffer = ""
            return self.redact(safe_text)

        if len(self.buffer) <= BUFFER_SIZE:
            return ""

        cutoff = len(self.buffer) - BUFFER_SIZE

        # Never split a detected PII match across the output boundary.
        for pattern in (EMAIL_PATTERN, SSN_PATTERN, CARD_PATTERN):
            for match in pattern.finditer(self.buffer):
                if match.start() < cutoff < match.end():
                    cutoff = match.start()

        safe_text = self.buffer[:cutoff]
        self.buffer = self.buffer[cutoff:]

        return self.redact(safe_text)