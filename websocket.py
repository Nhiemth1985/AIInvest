# Title:             AIInvest
# Author:            Nikodem Witt
# Date:              19.05.2021
# Version:           0.1
# Python_Version     3.9.5
"""
Main agenda of this program is automated trading within many stock market exchanges.
Program is using API to communicate with stock markets if possible.
Otherwise there are implementations that are used to communicate with markets if API is not available.
AIInvest is using complex mathematical equations and technical indicators to decide whether to sell or buy.
There are many possibilities of how to interpreter technical indicators that's why it is under development
that program will be capable of deciding which one to chose by predicting profitability of each.
Main markets to trade in are: Binance, BitMex and Nasdaq.

Requirements:
pip install python-binance
pip install matplotlib

"""
#   time module is used to generate a human readable time and date
from typing import List

import time
#   asyncio module is essential for binance websockets (which works in asynchronous mode)
import asyncio
#    binance websocket manager and async client modules
from binance import AsyncClient
from binance.streams import BinanceSocketManager
import matplotlib.pyplot as plt

class WebSocket:
	"""WebSocket class is responsible for:
	1) scraping data about specific pair from binance
	2) converting scraped data into desired format using filter
	How to use?
	First you need to initialize a trading pair to watch.
	Apply following filters into run function  to get data in format you like:
	More info about filter in help run function
	"""

	def __init__(self, crypto_pair):
		self.crypto_pair = crypto_pair

	async def binance_socket(self, filter_data):
		"""Function responsible for scraping live data from
		binance using websocket for specific crypto 'pair'
		This function works in asynchronous mode.
		Filters applied in run function are used here."""
		client = await AsyncClient.create()
		binance_socket_manager = BinanceSocketManager(client)

		#   Creates socket manager in socket trade mode with specific 'pair'
		trade_socket = binance_socket_manager.trade_socket(self.crypto_pair)

		#   Check if filter data type are an integer number, then convert type to int
		try:
			filter_data = int(filter_data)
		except ValueError:
			return print('INVALID FILTER!')

		#   starts receiving messages from web socket
		async with trade_socket as trade_socket_connection_manager:

			#   Asynchronous loop which is receiving live data from Binance WebSocket
			while True:
				received_data = await trade_socket_connection_manager.recv()

				#   Filters are applied here
				if filter_data == 0:
					# data in the following format (RAW):
					# {'e': 'trade', 'E': 1622975821586, 's': 'BTCUSDT', 't': 893630626, 'p': '35999.98000000', 'q': '0.00029400', 'b': 6334581192, 'a': 6334581308, 'T': 1622975821586, 'm': True, 'M': True}
					print(received_data)
					filename = (self.crypto_pair + "_DATA_RAW.txt")
					file2write = open(filename, 'a')
					file2write.write(str(str(received_data) + "\n"))
					file2write.close()

				elif filter_data == 1:
					# data in the following format (HUMAN READEABLE)
					# PRICE: "price"   TIME: "Y-m-d H:M:S.ms"
					received_data_price = str(received_data.get('p'))[:-6]
					received_data_time = received_data.get('T')
					formatted_data_time = WebSocket.epoch_time_to_human_date(received_data_time)
					print("PRICE:  " + str(received_data_price) + "  TIME:  " + formatted_data_time)
					filename = (self.crypto_pair + "_DATA_HUMAN.txt")
					file2write = open(filename, 'a')
					file2write.write(
						str("PRICE:  " + str(received_data_price) + "  TIME:  " + formatted_data_time) + "\n")
					file2write.close()

				elif filter_data == 2:
					# data in the following format (COMPRESSED FOR CALCULATION)
					# "price"+"Y-m-d-H-M-S-ms"+"quantity"
					received_data_price = str(received_data.get('p'))[:-6]
					received_data_time = received_data.get('T')
					received_data_quantity = received_data.get('q')
					formatted_data_time = WebSocket.epoch_time_to_date(received_data_time)
					print(str(received_data_price) + "+" + formatted_data_time)

					#Creating Y axis - price
					filename = (self.crypto_pair + "_DATA_CHART_Y.txt")
					file2write = open(filename, 'a')
					file2write.write(str(received_data_price + " "))
					file2write.close()

					#Creating X axis - date
					filename = (self.crypto_pair + "_DATA_CHART_X.txt")
					file2write = open(filename, 'a')
					file2write.write(str(formatted_data_time + " "))
					file2write.close()

				else:
					print('NOT VALID FILTER ARGUMENT')

				await client.close_connection()

	@staticmethod
	def epoch_time_to_human_date(epoch_time):
		"""Converts epoch time format into
		human friendly format.
		:param epoch_time:
		:return: Y-m-d H:M:S.ms
		"""
		epoch_time_date = str(epoch_time)[:-3]
		epoch_time_ms = str(epoch_time)[-3:]
		time_formatted = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(epoch_time_date)))
		return time_formatted + '.' + epoch_time_ms

	@staticmethod
	def epoch_time_to_date(epoch_time):
		"""Converts epoch time format into
		compressed version used in charts.
		:param epoch_time:
		:return: Y-m-d-H-M-S-ms
		"""
		epoch_time_date = str(epoch_time)[:-3]
		epoch_time_ms = str(epoch_time)[-3:]
		time_formatted = time.strftime('%Y%m%d%H%M%S', time.localtime(int(epoch_time_date)))
		return time_formatted + epoch_time_ms

	def run(self, filter_data):
		"""Should be provided with a filter argument:
		0 - to get data unfiltered
		1 - to get data with (PRICE:  price  TIME:  human_time) format
		2 - to get data in compressed format used in charts"""
		loop = asyncio.get_event_loop()
		loop.run_until_complete(WebSocket.binance_socket(self, filter_data))

	def chart(self):
		"""Function creating chart out of saved cryptopair data
		X = DATE     Y = PRICE"""
		#try:
		if True:
			#CREATING X LIST FROM FILE
			filename = (self.crypto_pair + "_DATA_CHART_X.txt")
			file = open(filename, 'r')
			lines = file.readlines()
			chart_x = []
			for l in lines:
				chart_x.append(l.split(" "))
			chart_x_float = []
			for values in chart_x:
				chart_x_float.append(float(values))

			print(chart_x_float)
			#CREATING Y LIST FROM FILE
			filename = (self.crypto_pair + "_DATA_CHART_Y.txt")
			file = open(filename, 'r')
			lines = file.readlines()
			chart_y = []
			for l in lines:
				chart_y.append(l.split(" "))
			chart_y = [int(i) for i in chart_x]
			print(chart_y)
			#CREATING CHART
			plt.bar(chart_x, chart_y)
			plt.show()

		#except:
		#	print("NO CRYPTOPAIR DATA\n"
		#	      "CAN'T CREATE CHART")


if __name__ == "__main__":
	print('Choose what you want to do:\n'
	      '	1 - scrap live data from Binance server and save it\n'
	      '	2 - Create chart out of already scraped data')
	user_input = input()
	if user_input == '1':
		print('All data are appended into corresponding files in txt format')
		print('Please provide valid binance crypto pair ex. BTCUSDT')
		crypto_pair = input()
		ws_var = WebSocket(crypto_pair)
		print('Please provide filter argument to view data')
		print('0 = raw data, 1 = human readable data, 2 = chart generating format')
		fil = input()
		print('Filter added, starting data scraping now...')
		ws_var.run(fil)
	elif user_input == '2':
		print('Choose cryptocurrency pair for chart:')
		crypto_pair = input()
		print('Creating chart...')
		WebSocket(crypto_pair).chart()
