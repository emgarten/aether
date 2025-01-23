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


def query_llm(prompt: str, system=SYSTEM_PROMPT, max_tokens=1024, chat=None) -> list:
    """
    If `chat` is None, this starts a new conversation using `system` and the `prompt`.
    If `chat` is provided, it's assumed to be the entire list of messages (the conversation).

    This method now returns the updated conversation list (messages), with the assistant's
    response appended at the end.
    """
    if not AZURE_OPENAI_API_KEY:
        raise ValueError("'AZURE_OPENAI_API_KEY' env var is not set. Unable to make requests to Azure OpenAI.")

    # If we're continuing a conversation, just append the new user message
    if chat is not None:
        chat.append({"role": "user", "content": prompt})
        messages = chat
    else:
        # Otherwise, start a brand new conversation
        messages = [
            {"role": "system", "content": [{"type": "text", "text": system}]},
            {"role": "user", "content": prompt},
        ]

    completion = client.chat.completions.create(model=DEPLOYMENT_NAME, messages=messages, max_tokens=max_tokens, temperature=0.7, top_p=0.95, frequency_penalty=0, presence_penalty=0, stop=None, stream=False)

    if hasattr(completion, "usage") and completion.usage is not None:
        logging.debug(f"Total tokens: {completion.usage.total_tokens} " f"Prompt tokens: {completion.usage.prompt_tokens} " f"Completion tokens: {completion.usage.completion_tokens}")

    # Get the assistant's response
    assistant_response = completion.choices[0].message.content

    # Append the assistant's response to the conversation
    messages.append({"role": "assistant", "content": assistant_response})

    # Return the entire updated conversation
    return messages


def get_last_message_content(chat: list) -> str:
    """
    Helper to return the content of the last message in the conversation.
    If the chat is empty or None, returns an empty string.
    """
    if not chat:
        return ""
    return chat[-1].get("content", "")


def query_json_llm(prompt: str, system=SYSTEM_PROMPT, max_tokens=4096, chat=None) -> any:
    """
    Calls `query_llm` and attempts to parse the result as JSON.
    This now also returns an updated conversation for continuity.
    """
    updated_chat = query_llm(prompt, system=system, max_tokens=max_tokens, chat=chat)
    # Extract the last message from the updated chat
    last_message = get_last_message_content(updated_chat)
    try:
        result_json = extract_first_json_block(last_message)
        parsed_result = json.loads(result_json)
        return parsed_result
    except Exception as e:
        logging.error(f"Failed to parse JSON from response! {e}\n{last_message}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Start a brand-new conversation
    conversation = [{"role": "system", "content": [{"type": "text", "text": SYSTEM_PROMPT}]}]

    print("Welcome to the Azure OpenAI Chat! (Type 'quit' to exit)\n")

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        # Query the LLM, continuing the conversation
        conversation = query_llm(user_input, chat=conversation)

        # Get the assistant's response from the updated conversation
        assistant_message = get_last_message_content(conversation)
        print(f"Assistant: {assistant_message}\n")
