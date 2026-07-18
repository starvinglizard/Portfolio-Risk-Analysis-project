import os
from dotenv import load_dotenv
from groq import Groq
import streamlit as st

load_dotenv()

api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)


def summarize_news(ticker, news_articles):
    if not news_articles:
        return "No recent news available to summarize."

    headlines_text = "\n\n".join(
        f"- {article['title']}\n  {article['summary']}" if article['summary'] else f"- {article['title']}"
        for article in news_articles
    )

    prompt = f"""Here is recent news coverage about {ticker}:

{headlines_text}

Based only on this coverage, write a short summary in this format:
Bull case: (2-3 sentences on positive themes present in this coverage)
Bear case: (2-3 sentences on negative/risk themes present in this coverage)

Do not predict future stock price direction. Only summarize themes actually present in this coverage. If the coverage is too limited or one-sided to build a balanced case, say so honestly rather than inventing the other side."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content