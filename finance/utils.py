import pandas as pd
import os
from .models import StockData
from django.conf import settings
import pickle

def calculate_moving_average(symbol):
    # get history data
    stock_data = StockData.objects.filter(symbol=symbol).order_by('date')

    # to pandas DataFrame
    data = pd.DataFrame.from_records(stock_data.values('date', 'close_price'))
    data['date'] = pd.to_datetime(data['date'])
    data.set_index('date', inplace=True)
    # x = 
    # stock_data = StockData.objects.filter(symbol=symbol).values('date', 'close_price').order_by('date')
    # print("Queried stock_data:", list(stock_data))
    # data = pd.DataFrame.from_records(stock_data)
    # data['date'] = pd.to_datetime(data['date'])


    # calculate the moving average
    data['50_MA'] = data['close_price'].rolling(window=50).mean()
    data['200_MA'] = data['close_price'].rolling(window=200).mean()

    return data

def backtest_strategy(symbol, initial_investment):
    data = calculate_moving_average(symbol)
    cash = float(initial_investment)
    stock_owned = 0
    total_value = []
    trades = 0
    max_drawdown = 0
    peak_value = cash

    for i in range(len(data)):
        current_price = data['close_price'].iloc[i]
        ma_50 = data['50_MA'].iloc[i]
        ma_200 = data['200_MA'].iloc[i]

        # Strategy-buy: lower than 50-day average and no owned stock
        if current_price < ma_50 and stock_owned == 0:
            stock_owned = cash // current_price  # buy as much as possible
            cash -= stock_owned * current_price
            trades += 1

        # Strategy-sell: higher than 200-day average and have stock
        elif current_price > ma_200 and stock_owned > 0:
            cash += stock_owned * current_price  # sell all
            stock_owned = 0
            trades += 1

        # calculate total value that day
        total_portfolio_value = cash + float(stock_owned * current_price)
        total_value.append(total_portfolio_value)

        # update the latest drawdown
        if total_portfolio_value > peak_value:
            peak_value = total_portfolio_value
        drawdown = (peak_value - total_portfolio_value) / peak_value
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    # calculate total return
    total_return = (float(total_value[-1]) - float(initial_investment)) / float(initial_investment) * 100
    return {
        'total_return': total_return,
        'max_drawdown': max_drawdown,
        'trades': trades
    }

def load_model(symbol):
    model_path = os.path.join(settings.BASE_DIR, 'ml_models', f'{symbol}_model.pkl')
    if not os.path.exists(model_path):
        raise ValueError(f"No pre-trained model found for {symbol}. Please train the model first.")
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model