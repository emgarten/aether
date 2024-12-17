import os

import requests

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = "https://juste.openai.azure.com/openai/deployments/gpt-4o-2/chat/completions?api-version=2024-02-15-preview"
SYSTEM_PROMPT = "You are an expert software support agent for azure iot operations. You are helping a customer troubleshoot an issue with their kubernetes pod logs."

headers = {
    "Content-Type": "application/json",
    "api-key": AZURE_OPENAI_API_KEY,
}


def query_llm(prompt: str, system=SYSTEM_PROMPT, max_tokens=1024) -> str:
    if not AZURE_OPENAI_API_KEY:
        raise ValueError("'AZURE_OPENAI_API_KEY' env var is not set. Unable to make requests to Azure OpenAI.")

    # Payload for the request
    payload = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": max_tokens,
    }

    # Send request
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")

    # Handle the response as needed (e.g., print or process)
    js = response.json()
    if len(js["choices"]) > 0:
        return js["choices"][0]["message"]["content"].strip()

    return None


# You can test this file directly to make sure calls are working.
if __name__ == "__main__":
    prompt = "Write a short paragraph describing what azure iot operations is."
    result = query_llm(prompt)

    if result:
        print("Response from Azure OpenAI:")
        print(result)
    else:
        print("Failed to get a response.")
