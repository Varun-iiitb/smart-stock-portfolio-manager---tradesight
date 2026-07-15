import os
import warnings
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

warnings.filterwarnings("ignore")

# Generated charts are written to the shared analytics_charts/charts folder
# (sibling of backend/), resolved from this file's location so it works
# regardless of CWD.
CHARTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analytics_charts', 'charts')
)


def apply_premium_theme(fig, title, yaxis_title=None, xaxis_title=None, show_legend=True):
    fig.update_layout(
        paper_bgcolor='#0a0c10',
        plot_bgcolor='#0a0c10',
        title={
            'text': title,
            'y': 0.93,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'family': 'Outfit, sans-serif', 'size': 18, 'color': '#f3f4f6'}
        },
        font=dict(family="Outfit, sans-serif", color="#9ca3af"),
        xaxis=dict(
            title=dict(text=xaxis_title, font=dict(family="Outfit, sans-serif", size=13, color="#9ca3af")) if xaxis_title else None,
            gridcolor='rgba(255, 255, 255, 0.05)',
            zerolinecolor='rgba(255, 255, 255, 0.08)',
            tickfont=dict(family="Inter, sans-serif", size=11, color="#9ca3af"),
            showgrid=True, showline=True,
            linecolor='rgba(255, 255, 255, 0.08)'
        ),
        yaxis=dict(
            title=dict(text=yaxis_title, font=dict(family="Outfit, sans-serif", size=13, color="#9ca3af")) if yaxis_title else None,
            gridcolor='rgba(255, 255, 255, 0.05)',
            zerolinecolor='rgba(255, 255, 255, 0.08)',
            tickfont=dict(family="Inter, sans-serif", size=11, color="#9ca3af"),
            showgrid=True, showline=True,
            linecolor='rgba(255, 255, 255, 0.08)'
        ),
        showlegend=show_legend,
        legend=dict(
            font=dict(family="Inter, sans-serif", size=11, color="#9ca3af"),
            bgcolor='rgba(10, 12, 16, 0.6)',
            bordercolor='rgba(255, 255, 255, 0.08)',
            borderwidth=1,
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ) if show_legend else None,
        margin=dict(t=80, b=40, l=60, r=40),
        hoverlabel=dict(
            bgcolor="#111620",
            bordercolor="#3a86ff",
            font=dict(family="Inter, sans-serif", size=12, color="#f3f4f6")
        ),
        hovermode="x unified"
    )


def _compute_indicators(df):
    """Build a feature matrix of common technical indicators from OHLCV data."""
    out = pd.DataFrame(index=df.index)
    close = df['Close']
    high = df['High']
    low = df['Low']
    volume = df['Volume']

    # Lagged returns
    for lag in [1, 2, 3, 5, 10]:
        out[f'ret_{lag}'] = close.pct_change(lag)

    # SMA ratios (close vs moving average)
    for w in [5, 10, 20, 50]:
        out[f'sma_ratio_{w}'] = close / close.rolling(w).mean() - 1

    # Trend strength: short SMA vs long SMA
    out['trend_5_50'] = close.rolling(5).mean() / close.rolling(50).mean() - 1

    # RSI(14)
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    out['rsi_14'] = 100 - 100 / (1 + rs)

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    out['macd'] = macd
    out['macd_signal'] = macd.ewm(span=9, adjust=False).mean()
    out['macd_hist'] = macd - out['macd_signal']

    # Bollinger position (z-score within 20-day band)
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    out['boll_pos'] = (close - sma20) / (2 * std20.replace(0, np.nan))

    # Recent return volatility
    out['vol_10'] = out['ret_1'].rolling(10).std()

    # Intraday range and close position
    out['hl_range'] = (high - low) / close
    out['close_pos'] = (close - low) / (high - low).replace(0, np.nan)

    # Volume ratio vs 20-day average
    out['vol_ratio'] = volume / volume.rolling(20).mean()

    return out


def _arima_forecast(close_series, steps=30):
    """Fit a small grid of ARIMA orders on log-prices and forecast `steps` ahead.
    Returns a DataFrame with columns ['mean', 'lower', 'upper'] indexed by future business days."""
    from statsmodels.tsa.arima.model import ARIMA

    # Use the last ~2 years; ARIMA gets less responsive on very long series
    s = close_series.tail(500).dropna()
    if len(s) < 50:
        return None

    log_s = np.log(s)

    candidates = [(1, 1, 1), (2, 1, 2), (1, 1, 0), (0, 1, 1), (5, 1, 0)]
    best = None
    best_aic = np.inf
    for order in candidates:
        try:
            model = ARIMA(log_s, order=order).fit()
            if model.aic < best_aic:
                best_aic = model.aic
                best = model
        except Exception:
            continue

    if best is None:
        return None

    try:
        fc = best.get_forecast(steps=steps)
        mean_log = fc.predicted_mean
        ci_log = fc.conf_int(alpha=0.05)
        lower_col = [c for c in ci_log.columns if 'lower' in c.lower()][0]
        upper_col = [c for c in ci_log.columns if 'upper' in c.lower()][0]

        future_idx = pd.date_range(
            start=close_series.index[-1] + pd.Timedelta(days=1),
            periods=steps,
            freq='B'
        )

        return pd.DataFrame({
            'mean': np.exp(mean_log.values),
            'lower': np.exp(ci_log[lower_col].values),
            'upper': np.exp(ci_log[upper_col].values)
        }, index=future_idx)
    except Exception:
        return None


def _write_chart(ticker_symbol, hist, forecast_df):
    fig = go.Figure()

    recent = hist.tail(120)
    if not recent.empty:
        fig.add_trace(go.Scatter(
            x=recent.index, y=recent['Close'],
            mode='lines', name='Historical Close',
            line=dict(color='#9ca3af', width=2)
        ))

    if forecast_df is not None and not forecast_df.empty:
        # Connect history to forecast visually
        bridge_x = [recent.index[-1], forecast_df.index[0]]
        bridge_y = [recent['Close'].iloc[-1], forecast_df['mean'].iloc[0]]
        fig.add_trace(go.Scatter(
            x=bridge_x, y=bridge_y,
            mode='lines', showlegend=False,
            line=dict(color='#3a86ff', width=2, dash='dot'),
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scatter(
            x=forecast_df.index, y=forecast_df['mean'],
            mode='lines', name='30-Day Forecast (ARIMA)',
            line=dict(color='#3a86ff', width=3, shape='spline', smoothing=1.3)
        ))
        fig.add_trace(go.Scatter(
            x=list(forecast_df.index) + list(forecast_df.index[::-1]),
            y=list(forecast_df['upper']) + list(forecast_df['lower'][::-1]),
            fill='toself',
            fillcolor='rgba(58, 134, 255, 0.15)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo='skip',
            name='95% Confidence Band'
        ))

    apply_premium_theme(
        fig,
        f"XGBoost + ARIMA Forecast - {ticker_symbol}",
        yaxis_title="Price", xaxis_title="Date"
    )
    fig.update_layout(height=500)

    os.makedirs(CHARTS_DIR, exist_ok=True)
    fig.write_html(os.path.join(CHARTS_DIR, "prediction.html"))


def data(ticker_symbol):
    """Predict next-day direction (XGBoost classifier on technical indicators)
    and a 30-day price-level forecast (ARIMA on log-prices).

    Writes analytics_charts/charts/prediction.html and returns a human-readable summary."""
    from xgboost import XGBClassifier
    from sklearn.metrics import accuracy_score

    hist = yf.Ticker(ticker_symbol).history(period="max")
    if hist.empty:
        _write_chart(ticker_symbol, hist, None)
        return f"No price history available for {ticker_symbol}."

    hist.index = pd.to_datetime(hist.index).tz_localize(None)
    for c in ['Dividends', 'Stock Splits']:
        if c in hist.columns:
            hist = hist.drop(columns=c)
    hist = hist.dropna(subset=['Close'])

    if len(hist) < 250:
        _write_chart(ticker_symbol, hist, _arima_forecast(hist['Close'], steps=30))
        return f"Only {len(hist)} trading days of history - not enough for a reliable classifier. Showing trend forecast only."

    feats = _compute_indicators(hist)
    target = (hist['Close'].shift(-1) > hist['Close']).astype(int)

    df = pd.concat([feats, target.rename('target')], axis=1)

    # The very last row has no known next-day target - it's what we want to predict
    pred_row = df.iloc[[-1]].copy()
    df = df.iloc[:-1].dropna()

    if df.empty:
        _write_chart(ticker_symbol, hist, _arima_forecast(hist['Close'], steps=30))
        return "Insufficient feature data after preprocessing. Showing trend forecast only."

    feature_cols = [c for c in df.columns if c != 'target']
    X = df[feature_cols]
    y = df['target']

    # Time-series split (no shuffling): last 20% is the holdout
    split = int(len(X) * 0.8)
    X_train, X_val = X.iloc[:split], X.iloc[split:]
    y_train, y_val = y.iloc[:split], y.iloc[split:]

    xgb_kwargs = dict(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        n_jobs=-1,
        eval_metric='logloss',
        tree_method='hist'
    )

    clf_eval = XGBClassifier(**xgb_kwargs)
    clf_eval.fit(X_train, y_train)
    val_acc = accuracy_score(y_val, clf_eval.predict(X_val))

    # Retrain on full history for the actual prediction
    clf_full = XGBClassifier(**xgb_kwargs)
    clf_full.fit(X, y)

    X_pred = pred_row[feature_cols]
    if X_pred.isna().any(axis=1).iloc[0]:
        X_pred = X.iloc[[-1]]  # fall back to last fully-formed row

    p_up = float(clf_full.predict_proba(X_pred)[0][1])
    direction = "UP" if p_up >= 0.5 else "DOWN"
    confidence = max(p_up, 1 - p_up)

    forecast_df = _arima_forecast(hist['Close'], steps=30)
    _write_chart(ticker_symbol, hist, forecast_df)

    last_price = float(hist['Close'].iloc[-1])
    target_30d = float(forecast_df['mean'].iloc[-1]) if forecast_df is not None and not forecast_df.empty else None

    arrow = "Up" if direction == "UP" else "Down"
    pieces = [
        f"XGBoost direction call for tomorrow: {arrow} ({confidence*100:.1f}% confidence).",
        f"Holdout accuracy: {val_acc*100:.1f}%.",
    ]
    if target_30d is not None:
        pct = (target_30d - last_price) / last_price * 100
        pieces.append(f"ARIMA 30-day price target: {target_30d:.2f} ({pct:+.2f}% vs last close {last_price:.2f}).")
    return " ".join(pieces)
