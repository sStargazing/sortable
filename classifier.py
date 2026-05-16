import base64
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
MODEL = "gemini-2.0-flash"

EXISTING_PROMPT = """Here are the available folders: {folders}.
Look at this screenshot and return ONLY the folder name it belongs in.
If nothing matches well, return "root"."""

LLM_PROMPT = """Here are the existing folders: {folders}.
Look at this screenshot. If it fits an existing folder well, return that folder name.
If not, return a short, clean new folder name (2-3 words max).
Return ONLY the folder name, nothing else."""


def classify(image_path: str, folders: list[str], mode: str) -> str:
    """Return the folder name for the given screenshot."""
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
