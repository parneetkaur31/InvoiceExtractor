import os
import json
import re
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_with_ai(text: str) -> dict:
    """
    AI fallback extraction for missing fields.
    Safe JSON parsing.
    """

    prompt = f"""
You are an invoice data extraction system.

Extract the following fields from the invoice text.

Return ONLY valid JSON.

If a field is missing return null.

Fields:
invoice_no
invoice_date
irn
order_id
order_date
title
hsn_sac
quantity
imei_serial
total
grand_total
sold_by_address
gstin
bill_to_address
ship_to_address

Invoice Text:
{text}
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        raw = response.choices[0].message.content.strip()

        if not raw:
            print("🔴 OpenAI returned empty response")
            return {}

        raw = re.sub(r"^```json|```$", "", raw, flags=re.IGNORECASE).strip()

        data = json.loads(raw)

        if isinstance(data, dict):
            return data
        else:
            return {}

    except Exception as e:

        print("🔴 OpenAI extraction failed:", e)
        return {}