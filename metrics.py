import pandas as pd

def calculate_stdev(returns):
    return returns.std()

def calculate_beta(asset_returns,benchmark_returns):
    combined = pd.concat([asset_returns,benchmark_returns],axis=1).dropna()     #.dropna() removes any value that is NaN. Axis = 1 tells program to use columns
    asset = combined.iloc[:, 0]
    benchmark = combined.iloc[:, 1]

    covariance = asset.cov(benchmark)
    benchmark_variance = benchmark.var()

    beta = covariance / benchmark_variance
    return beta

def calculate_sharpe(returns, monthly_rf):
    excess_return = returns.mean() - monthly_rf
    volatility = returns.std()
    sharpe = excess_return / volatility
    return sharpe

def calculate_treynor(returns, monthly_rf, beta):
    excess_return = returns.mean() - monthly_rf
    Treynor = excess_return / beta
    return Treynor

def calculate_parametric_var(returns, confidence_level=0.95):
    mean_return = returns.mean()
    stdev = returns.std()

    if confidence_level == 0.95:
        z = 2
    elif confidence_level == 0.99:
        z = 3
    else:
        raise ValueError("confidence_level must be 0.95 or 0.99")

    var = mean_return - (z * stdev)
    return var

#Testing area for functions

if __name__ == "__main__":                      # only runs when stub testing
    from data_fetch import get_price_data, get_monthly_returns, get_risk_free_rate

    tickers = ["AAPL", "MSFT", "TSLA"]
    prices = get_price_data(tickers)
    returns = get_monthly_returns(prices)

    benchmark_prices = get_price_data(["^GSPC"])
    benchmark_returns = get_monthly_returns(benchmark_prices)["^GSPC"]

    annual_rf, monthly_rf = get_risk_free_rate()

    for ticker in tickers:
        asset_returns = returns[ticker]

        stdev = calculate_stdev(asset_returns)
        beta = calculate_beta(asset_returns, benchmark_returns)
        sharpe = calculate_sharpe(asset_returns, monthly_rf)
        treynor = calculate_treynor(asset_returns, monthly_rf, beta)
        var_95 = calculate_parametric_var(asset_returns, confidence_level=0.95)
        var_99 = calculate_parametric_var(asset_returns, confidence_level=0.99)

        print(f"\n{ticker}")
        print(f"  Monthly StDev: {stdev:.2%}")
        print(f"  Beta: {beta:.2f}")
        print(f"  Sharpe: {sharpe:.2f}")
        print(f"  Treynor: {treynor:.2%}")
        print(f"  95% Parametric VaR: {var_95:.2%}")
        print(f"  99% Parametric VaR: {var_99:.2%}")

        
