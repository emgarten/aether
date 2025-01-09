import json
import logging
import os

from openai import AzureOpenAI

from util import extract_first_json_block

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_DEPLOYMENT_NAME")
SYSTEM_PROMPT = "You are an expert software support agent for azure iot operations. You are helping a customer troubleshoot an issue with their kubernetes pod logs."

headers = {
    "Content-Type": "application/json",
    "api-key": AZURE_OPENAI_API_KEY,
}

client = AzureOpenAI(
    azure_endpoint=ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-05-01-preview",
)


def query_llm(prompt: str, system=SYSTEM_PROMPT, max_tokens=1024) -> str:
    if not AZURE_OPENAI_API_KEY:
        raise ValueError("'AZURE_OPENAI_API_KEY' env var is not set. Unable to make requests to Azure OpenAI.")

    messages = [
        {"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT}]},
        {"role": "user", "content": prompt},
    ]

    completion = client.chat.completions.create(model=DEPLOYMENT_NAME, messages=messages, max_tokens=max_tokens, temperature=0.7, top_p=0.95, frequency_penalty=0, presence_penalty=0, stop=None, stream=False)

    return completion.choices[0].message.content


def query_json_llm(prompt: str, system=SYSTEM_PROMPT, max_tokens=4096) -> any:
    # Pass filter_prompt to query_llm and parse the result as JSON
    result = query_llm(prompt, system, max_tokens)
    try:
        result_json = extract_first_json_block(result)
        parsed_result = json.loads(result_json)
        return parsed_result
    except Exception as e:
        logging.error(f"Failed to parse JSON from response! {e}\n{result}")


# You can test this file directly to make sure calls are working.
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    prompt = "Write a short paragraph describing what azure iot operations is."
    result = query_llm(prompt)

    if result:
        logging.info("Response from Azure OpenAI:")
        logging.info(result)
    else:
        logging.info("Failed to get a response.")
