import pandas as pd
from streamlit import dataframe


def calculate_portfolio_returns(returns, weights):
    """
    Combines individual stock returns into a single weighted portfolio return series.

    returns: DataFrame with one column per ticker, one row per month
    weights: dict, e.g. {"AAPL": 0.5, "MSFT": 0.3, "TSLA": 0.2} (must sum to 1.0)
    """
    total_weight = sum(weights.values())

    if not (0.999 <= total_weight <= 1.001):
        raise ValueError(
            f"Weights must sum to 1.0, but they sum to {total_weight:.4f} instead."
        )

    weights_series = pd.Series(weights)
    selected_returns = returns[list(weights.keys())]
    portfolio_returns = selected_returns @ weights_series

    return portfolio_returns

def calculate_correlation_matrix(returns):
    return returns.corr()

def flag_high_correlations(correlation_matrix, threshold=0.6):
    tickers = correlation_matrix.columns

    for i in range(len(tickers) - 1):
        for j in range(i + 1, len(tickers)):
            ticker_a = tickers[i]
            ticker_b = tickers[j]
            correlation = correlation_matrix.iloc[i, j]    # iloc finds the part in the matrix

            if correlation > threshold:
                print(f"  WARNING: {ticker_a} and {ticker_b} are highly correlated ({correlation:.2f})")

# Quick manual test
if __name__ == "__main__":
    from data_fetch import get_price_data, get_monthly_returns, get_risk_free_rate
    from metrics import (
        calculate_stdev,
        calculate_beta,
        calculate_sharpe,
        calculate_treynor,
        calculate_parametric_var,
    )

    tickers = ["AAPL", "MSFT", "TSLA"]
    weights = {"AAPL": 0.5, "MSFT": 0.3, "TSLA": 0.2}

    prices = get_price_data(tickers)
    returns = get_monthly_returns(prices)

    benchmark_prices = get_price_data(["^GSPC"])
    benchmark_returns = get_monthly_returns(benchmark_prices)["^GSPC"]

    annual_rf, monthly_rf = get_risk_free_rate()

    portfolio_returns = calculate_portfolio_returns(returns, weights)

    print("Portfolio monthly returns:")
    print(portfolio_returns)

    stdev = calculate_stdev(portfolio_returns)
    beta = calculate_beta(portfolio_returns, benchmark_returns)
    sharpe = calculate_sharpe(portfolio_returns, monthly_rf)
    treynor = calculate_treynor(portfolio_returns, monthly_rf, beta)
    var_95 = calculate_parametric_var(portfolio_returns, confidence_level=0.95)
    var_99 = calculate_parametric_var(portfolio_returns, confidence_level=0.99)

    print("\nPORTFOLIO METRICS")
    print(f"  Monthly StDev: {stdev:.2%}")
    print(f"  Beta: {beta:.2f}")
    print(f"  Sharpe: {sharpe:.2f}")
    print(f"  Treynor: {treynor:.2%}")
    print(f"  95% Parametric VaR: {var_95:.2%}")
    print(f"  99% Parametric VaR: {var_99:.2%}")
    correlation_matrix = calculate_correlation_matrix(returns)
    print("\nCORRELATION MATRIX:")
    print(correlation_matrix)

    print("\nHIGH CORRELATION WARNINGS:")
    flag_high_correlations(correlation_matrix, threshold=0.7)