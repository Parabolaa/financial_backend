from django.test import TestCase
from django.urls import reverse
from .utils import backtest_strategy
from .models import StockData

class BacktestHTMLTestCase(TestCase):
    
    def test_backtest_page_renders_form(self):
        """test the display of backtest page renders form"""
        response = self.client.get(reverse('backtest', args=['IBM']))
        
        self.assertEqual(response.status_code, 200)
        
        # check whether the page include Initial Investment
        self.assertContains(response, 'Initial Investment')
        self.assertContains(response, '<form', count=1)  # whether there is form tag
        self.assertContains(response, '<button type="submit">Run Backtest</button>', html=True)

    def test_backtest_result_page(self):
        """test the display of test_backtest_result page"""
        # simulate a request
        response = self.client.post(reverse('backtest', args=['IBM']), {
            'initial_investment': 10000
        })

        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Total Return:')
        self.assertContains(response, 'Max Drawdown:')
        self.assertContains(response, 'Number of Trades:')