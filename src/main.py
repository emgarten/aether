import asyncio
import argparse
import os

from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from prompt import get_prompt

from log_plugin import LogPlugin

load_dotenv()

async def main():
    parser = argparse.ArgumentParser(description="Process log files from a specified root directory.")
    parser.add_argument("path", help="Path to the root folder containing log files or a support bundle zip")
    args = parser.parse_args()

    OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_API_DEPLOYMENT')
    OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
    OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    OPENAI_PROMPT = get_prompt('summarize.md', "")

    kernel = Kernel()

    chat_completion = AzureChatCompletion(
        api_key=OPENAI_KEY,
        deployment_name=OPENAI_DEPLOYMENT,
        endpoint=OPENAI_ENDPOINT,
    )
    kernel.add_service(chat_completion)

    kernel.add_plugin(
        LogPlugin(args.path),
        plugin_name="LogParser",
    )

    execution_settings = AzureChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
    history = ChatHistory()
    history.add_system_message(OPENAI_PROMPT)

    result = await chat_completion.get_chat_message_content(
        history,
        settings=execution_settings,
        kernel=kernel,
    )

    print(result)

if __name__ == "__main__":
    asyncio.run(main())
