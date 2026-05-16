import base64
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

EXISTING_PROMPT = """Available categories: {folders}

Look at this screenshot. Reply with ONLY the single category it belongs in.
If none fit, reply with exactly: root"""

LLM_PROMPT = """Existing categories: {folders}

Look at this screenshot. First identify what it shows, then:
- If the content is semantically related to an existing category, use that category.
- If no existing category fits the content at all, create a short descriptive label (2-3 words).

Examples of good matching: a VSCode window belongs in "Development Environment", a cat photo belongs in "Cat Photos".
Examples of bad matching: a cat photo does NOT belong in "Development Environment".

Reply with ONLY the category label. No explanation, no punctuation, nothing else."""


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
    return response.choices[0].message.content.strip()
