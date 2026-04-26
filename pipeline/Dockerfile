FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

# Pre-download FinBERT weights at build time so cold starts don't hit HuggingFace
RUN python -c "from transformers import pipeline; pipeline('text-classification', model='ProsusAI/finbert', tokenizer='ProsusAI/finbert', top_k=None)"

COPY . .

CMD ["python", "main.py"]
