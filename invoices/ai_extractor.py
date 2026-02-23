import os
import json
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_with_ai(text: str) -> dict:
    """
    Safe OpenAI extraction with defensive JSON parsing.
    Never crashes the app.
    """

    prompt = f"""
You are a data extraction system.

Extract the following fields from the invoice text below.
Return ONLY valid JSON.
If a field is missing, set it to null.

Fields:
invoice_no
invoice_date
order_id
gstin
grand_total

Invoice Text:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content.strip()

    if not raw:
        print("🔴 OpenAI returned empty response")
        return {}

    # 🔽 Remove ```json ``` wrappers if present
    raw = re.sub(r"^```json|```$", "", raw, flags=re.IGNORECASE).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print("🔴 OpenAI returned invalid JSON:")
        print(raw)
        return {}
