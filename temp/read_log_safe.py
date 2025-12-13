
import sys

with open("temp/verify_log.txt", "rb") as f:
    content = f.read()
    # Decode as much as possible, escape rest
    text = content.decode("utf-8", errors="replace")
    with open("temp/verify_log_clean.txt", "w", encoding="utf-8") as out:
        out.write(text)

