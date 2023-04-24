# Get Started
Train your own ChatGPT with external docs.

## Presiquites
- Python 3.9

## Prepare OpenAI API key

### Option 1 - OpenAI Paid account
Get the API directly from here: https://platform.openai.com/account/api-keys

### Option 2 - Azure OpenAI Service
1. Create a Azure OpenAI resource
1. Get the key and the endpoint 
1. Create a `text-embedding-ada-002(version 2)` model with name `text-embedding-ada-002` for embedding.
1. Create a `gpt-35-turbo` model with name `chat` for chat completion.

## Installation
```bash
pip install -r requirements.txt
cp .env.sample .env
```
Update the configuration in `.env`.

## Usage
### 1. Build index for the documents
Download existing vector index files or build a new one:
```bash
source .env
./cli.py build ../your_internal_docs doc_index.json
```

### 2. Ask questions
```bash
./cli.py ask "How to deploy jar package?"
```

### 3. Start the web API for Teams bot 
```bash
./web.py
```