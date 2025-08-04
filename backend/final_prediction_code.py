import yfinance as yf
import pandas as pd
import numpy as np
from prophet import Prophet
import os   

np.random.seed(42)

def data (ticker_symbol):
    sp500 = yf.Ticker(ticker_symbol)
    sp500 = sp500.history(period="max")

    sp500.index = pd.to_datetime(sp500.index)


    del sp500["Dividends"]
    del sp500["Stock Splits"]

    sp500["Tomorrow"] = sp500["Close"].shift(-1)
    sp500["Target"] = (sp500["Tomorrow"] > sp500["Close"]).astype(int)

    sp500 = sp500.loc["1990-01-01":].copy()

    sp500 = sp500.dropna(subset=sp500.columns[sp500.columns != "Tomorrow"])

    sp500.reset_index(inplace=True)

    df = sp500[['Date','Tomorrow']]

    df = df.rename(columns={'Date': 'ds','Tomorrow':'y'})
    df[['y']] = (df[['y']]-df[['y']].mean())/df[['y']].std()

    df['y'] = df['y'].fillna(df['y'].mean())
    df['ds'] = df['ds'].dt.tz_localize(None)

    split_date = '2023-01-01'

    train_df = df[df['ds'] < split_date]
    test_df = df[df['ds'] >= split_date]

    model = Prophet()
    #Fitting the model
    model.fit(train_df)

    # dataframe for predcition
    future = pd.concat([
        train_df[['ds']],
        test_df[['ds']]
    ]).drop_duplicates().sort_values('ds').reset_index(drop=True)
    future.dropna(inplace = True)

    prediction = model.predict(future)
    prediction = prediction[['ds', 'yhat']]

    #Model Accuracy

    mae = (df['y'] - prediction['yhat']).abs().mean()
    print(f'Mean Absolute Error: {mae}')

    print(df['y'].isna().sum(), "NaNs in test values")
    print(prediction['yhat'].isna().sum(), "NaNs in predicted values")

    from sklearn.metrics import mean_absolute_error

    mae = mean_absolute_error(df['y'].values, prediction['yhat'].values)
    print("MAE:", mae)

    model = Prophet()
    model.fit(df)

    future_period = model.make_future_dataframe(periods=1)
    prediction = model.predict(future_period)

    today_pred = prediction.iloc[-2]['yhat']
    tomorrow_pred = prediction.iloc[-1]['yhat']

    # Decision
    will_increase = tomorrow_pred > today_pred

    if will_increase:
        output_1 = "The model forecasts a likely increase in price for tomorrow"
    else:
        output_1 = "The model forecasts a likely decrease in price for tomorrow"
    

    fut = model.make_future_dataframe(periods= 7)
    pred = model.predict(fut)

    # today_pred_1 = pred.iloc[-7]['yhat']
    # week_later_pred = pred.iloc[-1]['yhat']

    import plotly.graph_objects as go

    # Generate future forecast
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    # Fix: Ensure date-only comparison
    last_date = df['ds'].max().date()
    future_forecast = forecast[forecast['ds'].dt.date > last_date]

    # Create Plotly figure
    fig = go.Figure()

    # Add predicted line (yhat)
    fig.add_trace(go.Scatter(
        x=future_forecast['ds'], y=future_forecast['yhat'],
        mode='lines',
        name='Predicted Price',
        line=dict(color='blue')
    ))

    # Add confidence interval (shaded region)
    fig.add_trace(go.Scatter(
        x=future_forecast['ds'].tolist() + future_forecast['ds'][::-1].tolist(),
        y=future_forecast['yhat_upper'].tolist() + future_forecast['yhat_lower'][::-1].tolist(),
        fill='toself',
        fillcolor='rgba(52, 152, 219, 0.4)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=False,
        name='Confidence Interval'
    ))

    # Layout
    fig.update_layout(
        title="Predicted Price for the Next 30 Days",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        height=500
    )
    fig.write_html("prediction.html")
    return output_1

