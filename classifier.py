import base64
import os

from dotenv import load_dotenv
from groq import Groq
import re

load_dotenv()

api_key=os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError(
        "Missing GROQ_API_KEY. Add it to your .env file or export it in Terminal."
    )

_client=Groq(api_key=api_key)

MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

EXISTING_PROMPT = """Available categories: {folders}

Look at this screenshot and choose the best matching category.

Rules:
- You MUST reply with one of the available categories exactly as written.
- Some categories may be nested paths like dog/birds.
- If the image clearly matches a nested category, reply with the full nested path.
- If no category fits, reply with exactly: root.

Reply with ONLY the category name. No explanation."""

LLM_PROMPT = """Existing categories: {folders}

Look at this screenshot. First identify what it shows, then:
- If the content is semantically related to an existing category, use that category.
- If no existing category fits the content at all, create a short descriptive label (2-3 words).

Examples of good matching: a VSCode window belongs in "Development Environment", a cat photo belongs in "Cat Photos".
Examples of bad matching: a cat photo does NOT belong in "Development Environment".

Reply with ONLY the category label. No explanation, no punctuation, nothing else."""


def clean_label(label: str) -> str:
    label=label.strip()

    # Keep letters, numbers, spaces, hyphens, underscores, and folder slashes
    label=re.sub(r"[^\w\s\-/]", "", label)

    # Remove duplicate spaces
    label=re.sub(r"\s+", " ", label)

    # Remove accidental starting/ending slashes
    label=label.strip("/")

    return label[:80]

def classify(image_path: str, folders: list[str], mode: str) -> str:
    folder_list = ", ".join(folders) if folders else "(none)"
    prompt = (EXISTING_PROMPT if mode == "existing" else LLM_PROMPT).format(
        folders=folder_list
    )

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    ext = os.path.splitext(image_path)[1].lower()
    media_type = "image/png" if ext == ".png" else "image/jpeg"

    response = _client.chat.completions.create(
        model=MODEL,
        max_tokens=64,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{image_data}"}},
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    )
    result=response.choices[0].message.content.strip()
    return clean_label(result)
