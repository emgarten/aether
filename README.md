# LLM based support bundle analyzer

![LLM Flow Background](docs/llm-flow-bg.png)

## Getting started

```bash
# Setup your env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Config
export AZURE_OPENAI_API_KEY=<your key>
export AZURE_OPENAI_ENDPOINT=<your url>

# linting and formatting
invoke lint

# Run
python3 ./src/main.py <path to zip> [--verbose]
```

## Flow

1. Clusters the logs to reduce them down since it can't send them all in the prompt
1. Creates an ID for each cluster and sends those to the LLM and asks it give back the list of IDs of only failure messages
1. Filters down to those IDs
1. Add context about which pod the error came from, occurrences, timestamp ranges
1. Sends those messages with context to the LLM and asks for a summary
