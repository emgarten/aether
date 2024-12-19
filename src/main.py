import asyncio
import argparse
import os

from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from log_plugin import LogPlugin

load_dotenv()

async def main():
    parser = argparse.ArgumentParser(description="Process log files from a specified root directory.")
    parser.add_argument("path", help="Path to the root folder containing log files or a support bundle zip")
    args = parser.parse_args()

    OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_API_DEPLOYMENT')
    OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_API_ENDPOINT")
    OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    OPENAI_PROMPT = "You are an expert software support agent for azure iot operations. You are helping a customer troubleshoot an issue with their kubernetes pod logs."

    kernel = Kernel()

    chat_completion = AzureChatCompletion(
        api_key=OPENAI_KEY,
        deployment_name=OPENAI_DEPLOYMENT,
        endpoint=OPENAI_ENDPOINT,
    )
    kernel.add_service(chat_completion)

    logPlugin = kernel.add_plugin(
        LogPlugin(args.path),
        plugin_name="LogParser",
    )

    digestFunction = logPlugin['supportBundleDigest']
    result = await kernel.invoke(digestFunction, input=OPENAI_PROMPT)

    print(result)

if __name__ == "__main__":
    asyncio.run(main())
