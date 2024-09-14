import openai as official_openai
import openai_manager
from openai_manager.utils import timeit

official_openai.api_key = "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"
openai_manager.api_key = "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"

import openai
openai.api_base = "http://localhost:8000/v1"
openai.api_key = "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"

# run like normal
prompt = ["Once upon a time, "] * 10
response = openai.Completion.create(
    model="text-davinci-003",
    prompt=prompt,
    max_tokens=20,
)
print(response["choices"][0]["text"])