# -*- coding: utf-8 -*-
"""CoinoneFetch.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1S8PBsQGsoyFuG-XXfr6qe4fsuobNwRdI
"""

import pandas as pd
import requests

# Define function to fetch data from Gate.io
def fetch_data_gateio(currency_pair, start, end, interval='1m', max_retries=3, retry_delay=5):
    # https://www.gate.io/docs/developers/apiv4/#market-candlesticks
    url = "https://api.gateio.ws/api/v4/spot/candlesticks"
    all_data = []
    interval_duration_seconds = 60  # 1 minute in seconds
    max_data_points = 800
    retries = 0
    while start < end and retries < max_retries:
        fetch_end = min(start + max_data_points *
                        interval_duration_seconds, end)
        params = {
            'currency_pair': currency_pair,
            'interval': interval,
            'from': start,
            'to': fetch_end
        }
        print(currency_pair)

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raises an exception for HTTP errors
            data = response.json()

            if isinstance(data, dict) and 'label' in data:
                print(
                    f"Error fetching data for {currency_pair}: {data['message']}")
                retries += 1
                time.sleep(retry_delay)
                continue

            for item in data:
                try:
                    all_data.append({
                        'time': pd.to_datetime(int(item[0]), unit='s'),
                        'volume': float(item[1]),
                        'close': float(item[2]),
                        'high': float(item[3]),
                        'low': float(item[4]),
                        'open': float(item[5])
                    })
                except ValueError as e:
                    print(f"Error processing data item {item}: {e}")
                    continue

            start = fetch_end
            retries = 0  # Reset retries on successful fetch
        except requests.RequestException as e:
            print(f"Request error: {e}")
            retries += 1
            time.sleep(retry_delay)

    if retries == max_retries:
        print(
            f"Max retries reached for {currency_pair}. Some data may be missing.")

    return all_data

start_timestamp = 1713873599000
num_data_points = -12000000
stop_timestamp = 1713614399000

list_ts=[]
for timestamps in range(start_timestamp, stop_timestamp, num_data_points):
              list_ts.append(timestamps)

#USDT
all_data_usdt = []
for timestamp in list_ts:
          #krw/usdt
              url_krw_usdt = f"https://api.coinone.co.kr/public/v2/chart/KRW/USDT?interval=1m&timestamp={timestamp}"
              response_krw_usdt = requests.get(url_krw_usdt)
              data_krw_usdt = response_krw_usdt.json()['chart']
              df_krw_usdt = pd.DataFrame(data_krw_usdt,columns=['timestamp', 'open', 'high', 'low', 'close', 'target_volume', 'quote_volume'])
              df_krw_usdt['timestamp'] = pd.to_datetime(df_krw_usdt['timestamp'],unit= 'ms')
              all_data_usdt.append(df_krw_usdt)
              #print(df_krw_usdt)

              df_usdt = pd.concat(all_data_usdt, ignore_index=True)

print(df_usdt)

#BTC
all_data_btc = []
for timestamp in list_ts:
          #krw/btc
              url_krw_btc = f"https://api.coinone.co.kr/public/v2/chart/KRW/BTC?interval=1m&timestamp={timestamp}"
              response_krw_btc = requests.get(url_krw_btc)
              data_krw_btc = response_krw_btc.json()['chart']
              df_krw_btc = pd.DataFrame(data_krw_btc,columns=['timestamp', 'open', 'high', 'low', 'close', 'target_volume', 'quote_volume'])
              df_krw_btc['timestamp'] = pd.to_datetime(df_krw_btc['timestamp'],unit= 'ms')
              all_data_btc.append(df_krw_btc)
              df_btc = pd.concat(all_data_btc, ignore_index=True)

print(df_btc)

# Create 'close' BTC/USDT DataFrame
df_btc_usdt = pd.DataFrame({
    'time': df_btc['timestamp'],  # Use timestamp from KRW/BTC or KRW/USDT DataFrame
    'coinone_usdt': df_usdt['close'],
    'coinone_btc': df_btc['close'],
    'btc_volume' : df_btc['target_volume']
})
print(df_btc_usdt)

# Fetch data from both platform
gateio_data = fetch_data_gateio(currency_pair="BTC_USDT",start=1713614399, end=1713873599)

# Convert json to dataframe
gate_io_df=pd.DataFrame(gateio_data)
gate_io_df

gate_io_data = gate_io_df[['time','volume','close']]
gate_io_data = gate_io_data.rename(columns={'volume':'gateio_volume','close':'gateio_btc'})
gate_io_data

# Merge the datasets on timestamp column
merged_data = pd.merge(gate_io_data, df_btc_usdt, on='time', how='inner')
merged_data.to_csv('out.csv', index=False)
print(merged_data)