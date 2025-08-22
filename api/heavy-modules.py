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
            # MODÜL 32: Get 24hr ticker data
            print("Modül 32: Fetching 24hr ticker...")
            response = requests.get('https://fapi.binance.com/fapi/v1/ticker/24hr')
            ticker_data = response.json()
            
            # MODÜL 33: Iterator + Filter (Make.com blueprint conditions)
            print("Modül 33: Filtering coins...")
            filtered_coins = []
            
            for coin in ticker_data:
                symbol = coin['symbol']
                quote_volume = float(coin['quoteVolume'])
                count = int(coin['count'])
                price_change_percent = float(coin['priceChangePercent'])
                
                # Make.com filter conditions
                if not symbol.endswith('USDT'):
                    continue
                if quote_volume < 2000000:
                    continue
                if count < 1000000:
                    continue
                if price_change_percent < 5:
                    continue
                
                # Priority coins check (Make.com'daki OR conditions)
                priority_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 
                                'ADAUSDT', 'XRPUSDT', 'DOTUSDT', 'LINKUSDT', 
                                'AVAXUSDT', 'MATICUSDT']
                
                if symbol in priority_coins or (quote_volume > 2000000 and count > 1000000 and price_change_percent > 5):
                    filtered_coins.append(coin)
            
            print(f"Filtered {len(filtered_coins)} coins from {len(ticker_data)} total")
            
            # MODÜL 39: Math calculation for each filtered coin
            print("Modül 39: Calculating percentages...")
            calculated_results = []
            
            for coin in filtered_coins:
                last_price = float(coin['lastPrice'])
                open_price = float(coin['openPrice'])
                
                # Make.com math: ((lastPrice - openPrice) / openPrice) * 100
                calculated_percentage = ((last_price - open_price) / open_price) * 100
                
                # Filter for >40% gainers (Make.com condition)
                if calculated_percentage > 40:
                    calculated_results.append({
                        'symbol': coin['symbol'],
                        'price_change': coin['priceChange'],
                        'calculated_percentage': calculated_percentage,
                        'current_price': last_price
                    })
            
            # MODÜL 82: Get klines for filtered coins
            print("Modül 82: Fetching klines...")
            klines_data = {}
            
            # Limit to top 10 to avoid too many API calls
            top_coins = calculated_results[:10]
            
            for coin_data in top_coins:
                symbol = coin_data['symbol']
                try:
                    # Get 1h klines with limit 6 (Make.com'daki settings)
                    klines_url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval=1h&limit=6"
                    klines_response = requests.get(klines_url)
                    klines = klines_response.json()
                    
                    klines_data[symbol] = klines
                    
                except Exception as e:
                    print(f"Error fetching klines for {symbol}: {e}")
                    klines_data[symbol] = []
            
            # Format output like Make.com text aggregator
            selected_coins_text = ""
            for coin_data in calculated_results:
                symbol = coin_data['symbol']
                price_change = coin_data['price_change']
                calculated_pct = coin_data['calculated_percentage']
                
                # Make.com format: "SYMBOL price_change calculated_percentage"
                selected_coins_text += f"{symbol} {price_change} {calculated_pct:.2f}\n"
            
            # Prepare final result
            result = {
                'success': True,
                'module_32_count': len(ticker_data),
                'module_33_filtered': len(filtered_coins),
                'module_39_calculated': len(calculated_results),
                'module_82_klines_count': len(klines_data),
                'selected_coins': selected_coins_text.strip(),
                'klines_data': klines_data,
                'summary': {
                    'total_symbols': len(ticker_data),
                    'filtered_symbols': len(filtered_coins),
                    'high_gainers': len(calculated_results),
                    'with_klines': len(klines_data)
                }
            }
            
            self.wfile.write(json.dumps(result, indent=2).encode())
            
        except Exception as e:
            print(f"Error: {e}")
            error_result = {
                'success': False,
                'error': str(e),
                'selected_coins': '',
                'module_32_count': 0,
                'module_33_filtered': 0,
                'module_39_calculated': 0,
                'module_82_klines_count': 0
            }
            self.wfile.write(json.dumps(error_result).encode())

    def do_GET(self):
        # Health check endpoint
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        health = {
            'status': 'healthy',
            'service': 'Heavy Modules (32,33,39,82)',
            'modules': ['24hr_ticker', 'filter_iterator', 'math_calculation', 'klines_data']
        }
        self.wfile.write(json.dumps(health).encode())

    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
