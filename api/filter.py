from http.server import BaseHTTPRequestHandler
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        try:
            # Binance API call
            response = requests.get('https://fapi.binance.com/fapi/v1/ticker/24hr')
            ticker_data = response.json()
            
            filtered_coins = []
            for coin in ticker_data:
                if (coin['symbol'].endswith('USDT') and 
                    float(coin['quoteVolume']) > 2000000 and
                    float(coin['priceChangePercent']) > 40):
                    
                    price_change = ((float(coin['lastPrice']) - float(coin['openPrice'])) / float(coin['openPrice'])) * 100
                    filtered_coins.append(f"{coin['symbol']} {price_change:.1f} {coin['priceChangePercent']}")
            
            result = {
                'success': True,
                'selected_coins': '\n'.join(filtered_coins),
                'count': len(filtered_coins)
            }
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            error_result = {'success': False, 'error': str(e), 'selected_coins': ''}
            self.wfile.write(json.dumps(error_result).encode())
