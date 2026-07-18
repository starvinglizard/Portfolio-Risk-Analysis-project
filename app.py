import streamlit as st
from ai_summary import summarize_news
from data_fetch import get_price_data, get_monthly_returns, get_risk_free_rate, get_recent_news
from metrics import (
    calculate_stdev,
    calculate_beta,
    calculate_sharpe,
    calculate_treynor,
    calculate_parametric_var,
)
from portfolio import (
    calculate_portfolio_returns,
    calculate_correlation_matrix,
)

def explain_stock(ticker, beta, sharpe, treynor, var_95):
    explanation = f"**In plain English:** "

    if beta > 1.2:
        explanation += f"{ticker} tends to swing more than the overall market. "
    elif beta < 0.8:
        explanation += f"{ticker} tends to be calmer than the overall market. "
    else:
        explanation += f"{ticker} tends to move roughly in line with the overall market. "

    if sharpe < 0:
        explanation += "Over this period, it underperformed a risk-free investment once its risk is accounted for. "
    elif sharpe < 0.5:
        explanation += "Its risk-adjusted return has been modest. "
    else:
        explanation += "It has delivered a solid return for the risk taken. "

    explanation += f"There is roughly a 5% chance {ticker} could lose more than {abs(var_95):.1%} of its value in a given month, based on this historical data."

    return explanation

st.title("Portfolio Risk Analyzer")
st.write("Enter your holdings below to see your portfolio's risk profile.")

tickers_input = st.text_input("Tickers (comma-separated)", "AAPL, MSFT, TSLA")
weights_input = st.text_input("Weights (comma-separated, must sum to 1.0)", "0.5, 0.3, 0.2")

if st.button("Analyze Portfolio"):
    st.session_state.analyzed = True
    st.session_state.tickers_input = tickers_input
    st.session_state.weights_input = weights_input

if st.session_state.get("analyzed", False):
    tickers = [t.strip().upper() for t in st.session_state.tickers_input.split(",")]
    weights_list = [float(w.strip()) for w in st.session_state.weights_input.split(",")]
    weights = dict(zip(tickers, weights_list))

    prices = get_price_data(tickers)
    returns = get_monthly_returns(prices)

    benchmark_prices = get_price_data(["^GSPC"])
    benchmark_returns = get_monthly_returns(benchmark_prices)["^GSPC"]

    annual_rf, monthly_rf = get_risk_free_rate()


    portfolio_returns = calculate_portfolio_returns(returns, weights)

    stdev = calculate_stdev(portfolio_returns)
    beta = calculate_beta(portfolio_returns, benchmark_returns)
    sharpe = calculate_sharpe(portfolio_returns, monthly_rf)
    treynor = calculate_treynor(portfolio_returns, monthly_rf, beta)
    var_95 = calculate_parametric_var(portfolio_returns, confidence_level=0.95)
    var_99 = calculate_parametric_var(portfolio_returns, confidence_level=0.99)

    st.subheader("Portfolio Risk Metrics")
    st.write(f"**Monthly StDev:** {stdev:.2%}")
    st.write(f"**Beta:** {beta:.2f}")
    st.write(f"**Sharpe Ratio:** {sharpe:.2f}")
    st.write(f"**Treynor Ratio:** {treynor:.2%}")
    st.write(f"**95% Parametric VaR:** {var_95:.2%}")
    st.write(f"**99% Parametric VaR:** {var_99:.2%}")

    st.subheader("Individual Stock Reports")

    for ticker in tickers:
        asset_returns = returns[ticker]

        asset_stdev = calculate_stdev(asset_returns)
        asset_beta = calculate_beta(asset_returns, benchmark_returns)
        asset_sharpe = calculate_sharpe(asset_returns, monthly_rf)
        asset_treynor = calculate_treynor(asset_returns, monthly_rf, asset_beta)
        asset_var_95 = calculate_parametric_var(asset_returns, confidence_level=0.95)

        with st.expander(f"{ticker} — Risk Report"):
            st.write(f"**Monthly StDev:** {asset_stdev:.2%}")
            st.write(f"**Beta:** {asset_beta:.2f}")
            st.write(f"**Sharpe Ratio:** {asset_sharpe:.2f}")
            st.write(f"**Treynor Ratio:** {asset_treynor:.2%}")
            st.write(f"**95% Parametric VaR:** {asset_var_95:.2%}")

            st.write(explain_stock(ticker, asset_beta, asset_sharpe, asset_treynor, asset_var_95))

            st.write("**Recent News:**")
            news_articles = get_recent_news(ticker, max_articles=10)

            if news_articles:
                for article in news_articles[:3]:
                    st.markdown(f"- [{article['title']}]({article['link']})")

                st.write("**AI Summary:**")
                with st.spinner("Summarizing news..."):
                    summary = summarize_news(ticker, news_articles)
                st.write(summary)
            else:
                st.write("No recent news found.")

    st.subheader("Correlation Matrix")
    show_matrix = st.checkbox("Show correlation matrix")

    correlation_matrix = calculate_correlation_matrix(returns)

    if show_matrix:
        def color_correlation(value):
            if value == 1:
                return ""
            elif value > 0.6:
                return "background-color: #ff4b4b; color: white"
            elif value > 0.4:
                return "background-color: #ffd93d; color: black"
            else:
                return "background-color: #4caf50; color: white"

        styled_matrix = correlation_matrix.style.map(color_correlation)
        st.dataframe(styled_matrix)

    st.subheader("Diversification Check")
    tickers_list = correlation_matrix.columns
    found_warning = False

    for i in range(len(tickers_list) - 1):
        for j in range(i + 1, len(tickers_list)):
            ticker_a = tickers_list[i]
            ticker_b = tickers_list[j]
            correlation = correlation_matrix.iloc[i, j]

            if correlation > 0.6:
                found_warning = True
                st.warning(
                    f"**{ticker_a} and {ticker_b}** are highly correlated ({correlation:.2f}). "
                    f"They tend to move together, so holding both may not reduce your risk as much as expected."
                )


    if not found_warning:
        st.success("No highly correlated pairs found — your portfolio looks reasonably diversified.")