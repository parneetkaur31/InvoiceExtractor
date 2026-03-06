import re

REQUIRED_FIELDS = [
    "invoice_no",
    "invoice_date",
    "grand_total",
]

def extract_fields(text):

    data = {}

    patterns = {

        "invoice_no": [
            r"invoice\s*number\s*#?\s*([A-Z0-9\-]+)",
            r"invoice\s*no\.?\s*[:\-]?\s*([A-Z0-9\-]+)",
        ],

        "invoice_date": [
            r"invoice\s*date\s*[:\-]?\s*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})"
        ],

        "irn": [
            r"\birn\b\s*[:\-]?\s*([A-Z0-9]{10,})"
        ],

        "order_id": [
            r"order\s*id\s*[:\-]?\s*([A-Z0-9\-]+)"
        ],

        "order_date": [
            r"order\s*date\s*[:\-]?\s*([0-9]{2}[-/][0-9]{2}[-/][0-9]{4})"
        ],

        "gstin": [
            r"gstin\s*[-:]?\s*([0-9A-Z]{15})"
        ],

        "hsn_sac": [
            r"hsn[/\s]*sac\s*[:\-]?\s*([0-9]+)"
        ],

        "quantity": [
            r"qty\s*[:\-]?\s*([0-9]+)",
            r"quantity\s*[:\-]?\s*([0-9]+)"
        ],

        "imei_serial": [
            r"(?:imei|serial\s*no)\s*[:\-]?\s*([A-Z0-9\-]{6,})"
        ],

        "total": [
            r"\btotal\b\s*[₹Rs\.]*\s*([0-9,]+\.\d{2})",
            r"\btotal\b\s*[₹Rs\.]*\s*([0-9,]+)"
        ],

        "grand_total": [
            r"grand\s*total\s*[₹Rs\.]*\s*([0-9,]+\.\d{2})",
            r"grand\s*total\s*[₹Rs\.]*\s*([0-9,]+)"
        ],

        "title": [
            r"title\s*[:\-]?\s*(.+)"
        ],

        "sold_by_address": [
            r"sold\s*by\s*[:\-]?\s*(.+)"
        ],

        "bill_to_address": [
            r"bill\s*to\s*[:\-]?\s*(.+)"
        ],

        "ship_to_address": [
            r"ship\s*to\s*[:\-]?\s*(.+)"
        ]
    }

    for field, regex_list in patterns.items():

        for regex in regex_list:

            match = re.search(regex, text, re.IGNORECASE)

            if match:
                data[field] = match.group(1).strip()
                break

    return data


def learn_rule_from_text(field, value, text):
    """
    Learns a simple regex rule for a field based on where
    the AI-extracted value appears in the invoice text.
    """

    if value is None:
        return None

    value_str = str(value).strip()

    if not value_str:
        return None

    for line in text.splitlines():

        if value_str in line:

            anchor = line.replace(value_str, "").strip()[:60]

            escaped_anchor = re.escape(anchor)
            escaped_value = re.escape(value_str)

            regex = rf"{escaped_anchor}\s*({escaped_value})"

            return {
                "field_name": field,
                "anchor": anchor,
                "regex": regex,
            }

    return None