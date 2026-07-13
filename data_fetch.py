import yfinance as yf
import pandas as pd

def get_price_data(tickers, period="2y", interval="1mo"):
    """
    Fetch historical adjusted close prices for one or more tickers.

    tickers: list of strings, e.g. ["AAPL", "MSFT", "TSLA"]
    period: how far back to pull data, e.g. "1y", "2y", "5y"
    interval: candle spacing, e.g. "1d", "1wk", "1mo"
    """
    data = yf.download(tickers, period=period, interval=interval, threads=False)["Close"]

    # If only one ticker is passed, yfinance returns a Series instead of a DataFrame
    if isinstance(data, pd.Series):
        data = data.to_frame(name=tickers[0])

    return data


def get_monthly_returns(price_data):
    """
    Convert price data into monthly percentage returns.
    Drops columns that are entirely missing, then drops any remaining incomplete rows.
    """
    price_data = price_data.dropna(axis=1, how="all")  # drop tickers that failed entirely
    returns = price_data.pct_change().dropna()
    return returns


def get_risk_free_rate():
    """
    Fetch the current annualized 13-week US T-bill rate (^IRX) and
    convert it to a monthly rate.
    """
    tbill = yf.Ticker("^IRX")
    hist = tbill.history(period="5d")
    annual_rf = hist["Close"].iloc[-1] / 100
    monthly_rf = annual_rf / 12
    return annual_rf, monthly_rf

def get_recent_news(ticker, max_articles=10):
    """
    Fetch recent news headlines (and summaries, if available) for a given ticker.
    """
    stock = yf.Ticker(ticker)
    news_items = stock.news

    articles = []
    for item in news_items[:max_articles]:
        content = item.get("content", {})
        title = content.get("title", "No title available")
        summary = content.get("summary", "")
        link = content.get("canonicalUrl", {}).get("url", "")
        articles.append({"title": title, "summary": summary, "link": link})

    return articles



# Quick manual test — only runs when you execute this file directly
if __name__ == "__main__":
    tickers = ["AAPL", "MSFT", "TSLA"]

    prices = get_price_data(tickers)
    print("PRICES:")
    print(prices.tail())

    returns = get_monthly_returns(prices)
    print("\nMONTHLY RETURNS:")
    print(returns.tail())

    annual_rf, monthly_rf = get_risk_free_rate()
    print(f"\nRISK-FREE RATE: annual={annual_rf:.4f}, monthly={monthly_rf:.4f}")
