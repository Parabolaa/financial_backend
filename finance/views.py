import requests
import pandas as pd
from django.shortcuts import render
from django.http import JsonResponse
from .models import StockData, PredictionData
from datetime import datetime, timedelta
from requests.exceptions import RequestException
from .forms import BacktestForm
from .utils import backtest_strategy, load_model
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image

def main_page(request):
    return render(request, 'finance/main.html')

def fetch_stock_data(request, symbol):
    API_KEY = 'PJECPCIPFIW7ZUU7'
    BASE_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY'
    INTERVAL = '5min'
    # extended_hours = 'false'
    month_limit = 24  # last 2 years

    # calculate month range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # last 2 years

    # standardize as YYYY-MM
    months = [(start_date + timedelta(days=30*i)).strftime('%Y-%m') for i in range(month_limit)]

    stock_data = []
    
    for month in months:
        url = f'{BASE_URL}&symbol={symbol}&interval={INTERVAL}&apikey={API_KEY}&month={month}'
        try:
            response = requests.get(url)
            response.raise_for_status()  # HTTP error
            data = response.json()
        except RequestException as e:
            # network or api request error
            return render(request, 'finance/error.html', {'error': 'Failed to fetch data: ' + str(e)})
        
        # rate limit or other api error
        if 'Note' in data:
            return render(request, 'finance/error.html', {'error': 'API rate limit exceeded, please try again later.'})
        
        # retrieve data
        time_series = data.get(f'Time Series ({INTERVAL})', {})

        # parse and store data
        for date_str, values in time_series.items():
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            stock_data.append({
                'date': date,
                'open_price': values['1. open'],
                'close_price': values['4. close'],
                'high_price': values['2. high'],
                'low_price': values['3. low'],
                'volume': values['5. volume'],
            })
            
            # store in database
            StockData.objects.update_or_create(
                symbol=symbol,
                date=date,
                defaults={
                    'open_price': values['1. open'],
                    'high_price': values['2. high'],
                    'low_price': values['3. low'],
                    'close_price': values['4. close'],
                    'volume': values['5. volume'],
                }
            )
    
    return render(request, 'finance/fetch_data.html', {
        'symbol': symbol,
        'data': stock_data
    })

def backtest_view(request, symbol):
    if request.method == 'POST':
        form = BacktestForm(request.POST)
        if form.is_valid():
            initial_investment = form.cleaned_data['initial_investment']
            result = backtest_strategy(symbol, initial_investment)
            return render(request, 'finance/backtest_result.html', {
                'symbol': symbol,
                'result': result,
                'form': form,
                'initial_investment': str(initial_investment)
            })
    else:
        form = BacktestForm()

    return render(request, 'finance/backtest.html', {'form': form, 'symbol': symbol})

def predict_stock_prices(request, symbol):
    try:
        model = load_model(symbol)
        stock_data = StockData.objects.filter(symbol=symbol).order_by('date')

        if not stock_data.exists():
            return render(request, 'finance/error.html', {
                "error": "No data found for symbol."
            })

        historical_prices = pd.DataFrame.from_records(stock_data.values('date', 'close_price'))
        historical_prices['date'] = pd.to_datetime(historical_prices['date'])

        # generate column 'days' representing days that start at the first date
        # generate characteristic for days
        historical_prices['days'] = (historical_prices['date'] - historical_prices['date'].min()).dt.days
        last_day = historical_prices['days'].max()

        # generate the future 30 days' charecteristics
        future_days = pd.DataFrame({'days': range(last_day + 1, last_day + 31)})  # days represnts future 30 days
        future_predictions = model.predict(future_days) # predict

        # generate the actual date
        last_date = historical_prices['date'].max()
        future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=30)

        # store the result to database
        for i in range(30):
            PredictionData.objects.create(
                symbol=symbol,
                date=future_dates[i],
                predicted_price=future_predictions[i]
            )

        predictions = [
            {"date": str(future_dates[i].date()), "predicted_price": future_predictions[i]}
            for i in range(30)
        ]
        actual_data = [{"date": str(data.date), "price": data.close_price} for data in stock_data]
        request.session[f"{symbol}_actual"] = actual_data
        request.session[f"{symbol}_predicted"] = predictions
        return render(request, 'finance/predict.html', {
            'symbol': symbol,
            'predictions': predictions
        })

    except Exception as e:
        return render(request, 'finance/error.html', {
            "error": str(e)
        })

def generate_stock_comparison_chart(symbol, predicted_data):
    # get predicted data
    predicted_dates = [data['date'] for data in predicted_data]
    predicted_prices = [data['predicted_price'] for data in predicted_data]

    # generate chart
    plt.figure(figsize=(14, 7), dpi=150)
    plt.plot(predicted_dates, predicted_prices, label='Predicted Prices', color='red', linestyle='--', marker='x')
    plt.title(f'{symbol} Stock Price Predictions')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.xticks(rotation=45)
    plt.legend()

    # save to buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer

def generate_report(request, symbol):
    predicted_data = request.session.get(f"{symbol}_predicted")
    chart_buffer = generate_stock_comparison_chart(symbol, predicted_data)

    # convert the image to ImageReader form that suits ReportLab
    pil_image = Image.open(chart_buffer)
    chart_image = ImageReader(pil_image)

    # generate PDF report
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{symbol}_report.pdf"'
    p = canvas.Canvas(response, pagesize=landscape(letter))  # 使用 landscape 设置横向页面
    p.setFont("Helvetica", 12)

    p.drawString(100, 550, f"{symbol} Stock Price Prediction Report")
    p.drawImage(chart_image, 100, 150, width=600, height=300)
    p.showPage()
    p.save()

    return response

def generate_report_json(request, symbol):
    predicted_data = request.session.get(f"{symbol}_predicted")

    return JsonResponse({
        "symbol": symbol,
        "predicted_prices": predicted_data
    })

def generate_backtest_report(request, symbol, initial_investment):
    backtest_result = backtest_strategy(symbol, initial_investment)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{symbol}_backtest_report.pdf"'

    p = canvas.Canvas(response, pagesize=landscape(letter))
    p.setFont("Helvetica", 12)

    p.drawString(100, 550, f"{symbol} Stock Backtest Report")
    p.drawString(100, 500, f"Initial Investment: ${initial_investment}")
    p.drawString(100, 480, f"Total Return: {backtest_result['total_return']:.2f}%")
    p.drawString(100, 460, f"Max Drawdown: {backtest_result['max_drawdown']:.2f}%")
    p.drawString(100, 440, f"Trades Executed: {backtest_result['trades']}")
    p.showPage()
    p.save()

    return response

def generate_backtest_json(request, symbol, initial_investment):
    backtest_result = backtest_strategy(symbol, initial_investment)
    actual_data = StockData.objects.filter(symbol=symbol).order_by('date').values('date', 'close_price')
    predicted_data = PredictionData.objects.filter(symbol=symbol).order_by('date').values('date', 'predicted_price')

    return JsonResponse({
        "symbol": symbol,
        "initial_investment": initial_investment,
        "total_return": backtest_result['total_return'],
        "max_drawdown": backtest_result['max_drawdown'],
        "trades": backtest_result['trades'],
        "predicted_prices": list(predicted_data),
        "actual_prices": list(actual_data)
    })