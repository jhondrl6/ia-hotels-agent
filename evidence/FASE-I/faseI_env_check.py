import re

KEYS = (
    "PAGESPEED_API_KEY",
    "GOOGLE_PAGESPEED_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_MAPS_API_KEY",
    "SERPAPI_KEY",
)

text = open(".env", encoding="utf-8").read()
for key in KEYS:
    match = re.search(r"^" + key + r"\s*=\s*(.*)", text, re.M)
    if not match:
        print(f"{key} = ABSENT")
        continue
    value = match.group(1).strip().strip('"').strip("'")
    n = len(value)
    verdict = "ABSENT" if n == 0 else ("PLACEHOLDER" if n < 10 else "OK")
    print(f"{key} len={n} {verdict}")
