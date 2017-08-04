#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests,time, json
import pandas as pd
import numpy as np
import math

# starURL = "https://114.55.157.119"
starURL = "https://star.sse.com.cn"


def getEtfCurrentPrice(s):
	#返回float型的etf现价
	try:
		url = starURL + "/mtpapi/rest/lastMarketData"
		payload = {'stockCode' : '510050'}
		r = s.post(url, json=payload)
		j = json.loads(r.text)
	except:
		return 0
	else:
		return float(j['lastTradePrice'])

def collectData(stockCode):
	#采集每日现货价格波动
	try:
	    startTime = time.time()
	    url = starURL+"/mkdapi/mktdata/stockKlineData?stockCode=%d"%stockCode
	    r = requests.get(url)
	    dic = json.loads(r.content)
	    import csv
	    saveDataUrl = "/Users/bill/Documents/intern_sseTech/%d%s.csv" % (stockCode, time.strftime('%Y%m%d',time.localtime(time.time())))
	    with open(saveDataUrl,'wb') as csvfile:
	        dataWriter = csv.writer(csvfile);dataWriter.writerow(('time','price', 'amount'))
	    	for data in dic['line']:
	        	dataWriter.writerow(data)
	    finishTime = time.time()
	    runningTime = finishTime - startTime
	    print "Finished, %d running time is %ds" % (stockCode, runningTime)
	except:
		return 0
	else:
		return 1

def computeTodayVix(stockCode):
	#计算ETF今日波动率
	try:
		pri = []
		payload = {'stockCode': '%d' % stockCode}
		r = requests.get(starURL+"/mkdapi/mktdata/stockKlineData", payload)
		j = json.loads(r.text)
		count = 0
		for i in j['line']:
			pri.append(i[1])
		pre = 0
		u_list = []
		u_total = 0
		u_amount = 0
		total = 0
		for price in pri:
			if pre != 0:
				u = (math.fabs(price-pre))/pre
				u_total = u_total + u
				u_amount = u_amount + 1
				u_list.append(u)
			pre = price
		u_average = u_total/u_amount
		for data in u_list:
			total = total + math.fabs(data - u_average)
		vix = math.sqrt(total / (u_amount - 1))
	except:
		return 0
	else:
		return vix

def computeDailyVixInHistory(stockCode):
	#计算历史数据中每一天的波动率
	import os
	try:
		path = "/Users/bill/Documents/intern_sseTech/%d"%stockCode
		files = os.listdir(path)
		s = []
		for fil in files:
			if not os.path.isdir(fil):
				if fil[0] != '.':
					# print fil
					df = pd.read_csv(path+'/'+fil)
					pre = 0
					u_list = []
					u_total = 0
					u_amount = 0
					total = 0
					for price in df['price']:
						if pre != 0:
							u = (math.fabs(price-pre))/pre
							u_total = u_total + u
							u_amount = u_amount + 1
							u_list.append(u)
						pre = price
					u_average = u_total/u_amount
					for data in u_list:
						total = total + math.fabs(data - u_average)
					vix = math.sqrt(total / (u_amount - 1))
					s.append(vix)
	except:
		return 0
	else:
		return s

def getDailyEtfPrice(stockCode):
	#收集历史上每一天的etf收盘价，返回一个列表
	import os
	try:
		path = "/Users/bill/Documents/intern_sseTech/%d"%stockCode
		files = os.listdir(path)
		print files
		s = []
		for fil in files:
			if not os.path.isdir(fil):
				if fil[0] != '.':
					df = pd.read_csv(path+'/'+fil)
					s.append(df['price'][239])
	except:
		return 0
	else:
		return s

def determineTrend(priceList):
	#传入价格列表，判断价格趋势趋势
	total = 0
	for price in priceList:
		total = total + price
	average = total / len(priceList)
	print average
	high = 0
	low = 0
	for price in priceList:
		print price
		if price > average:
			high = high + 1
		else:
			low = low + 1
	if high/low <= 3/7:
		return 0 #bear
	elif high/low <= 1 and high/low > 3/7:
		return 1
	elif high/low > 1 and high/low < 7/3:
		return 2
	else:
		return 3

def computeLongVixInHistory(stockCode):
	#计算过往所有的ETF波动率
	import os
	try:
		path = "/Users/bill/Documents/intern_sseTech/%d"%stockCode
		files = os.listdir(path)
		s = []
		for fil in files:
			if not os.path.isdir(fil):
				if fil[0] != '.':
					print fil
					df = pd.read_csv(path+'/'+fil)
					s.append(df['price'][239])
		pre = 0
		u_total = 0
		u_amount = 0
		u_list = []
		total = 0
		for price in s:
			if pre != 0:
				u = (math.fabs(price - pre))/pre
				print u
				u_total = u_total + u
				u_amount = u_amount + 1
				u_list.append(u)
			pre = price
		u_average = u_total/u_amount
		print 'average:%f' %  u_average
		print u_list
		for data in u_list:
			total = total +math.fabs(data - u_average)
		vix = math.sqrt(total / (u_amount - 1))
	except:
		return 0
	else:
		return vix

def getEtf50BuyingAndSellingPrice():
	#获得50etf现货五档行情中交易量最大的卖价和买价
	payload = {'stockCode': '510050'}
	try:
		r = requests.post(starURL+"/mtpapi/rest/marketData", json = payload)
		j = json.loads(r.text)
		# print j
		EtfFiveFileBuyingAndSelling =  j['data']
		tempSellingPrice = 0
		tempSellingNum = 0
		for tempDict in EtfFiveFileBuyingAndSelling:
			if tempDict['type'] == 'sell' and tempDict['num'] > tempSellingNum:
				tempSellingPrice = tempDict['price']
		tempBuyingPrice = 0
		tempBuyingNum = 0
		for tempDict in EtfFiveFileBuyingAndSelling:
			if tempDict['type'] == 'buy' and tempDict['num'] > tempBuyingNum:
				tempBuyingPrice = tempDict['price']
	except:
		return 0, 0
	else:
		return float(tempSellingPrice), float(tempBuyingPrice)

def getOptionPriceAndStatics(month):
	#获取期权T型报价
	dictionaryT = {}
	month = str(month)
	payloada = {'underlyingCode': '510050', 'month': month, 'type': 'A'}
	payloadb = {'underlyingCode': '510050', 'month': month, 'type': 'B'}
	payloadc = {'underlyingCode': '510050', 'month': month, 'type': 'C'}
	try:
		ra = requests.get(starURL+"/mkdapi/optdata/newTMarketData", payloada)
		ja = json.loads(ra.text)
		rb = requests.get(starURL+"/mkdapi/optdata/newTMarketData", payloadb)
		jb = json.loads(rb.text)
		rc = requests.get(starURL+"/mkdapi/optdata/newTMarketData", payloadc)
		jc = json.loads(rc.text)
		dic ={}
		dic['month'] = month
		dic['a'] = ja['list']
		dic['b'] = jb['list']
		dic['c'] = jc['list']
		# print dic['a'][8][7]
	except:
		return 0
	else:
		return dic

def getThisMonthAndNextMonth():
	#获取期权到期月份
	thisMonth = time.strftime('%Y%m',time.localtime(time.time()))
	if thisMonth[4:6] < '12':
		nextMonth = str(int(thisMonth) + 1)
	else:
		nextMonth = str(int(thisMonth[0:4])+1) + '01'
	if thisMonth[4:6] < '11':
		futureMonth = str(int(thisMonth) + 2)
	else:
		futureMonth = str(int(thisMonth[0:4])+1) + '%2d'%(12-int(thisMonth[4:6]))
	if thisMonth[4:6] < '8':
		futureMonth1 = str(int(thisMonth) + 5)
	else:
		futureMonth1 = str(int(thisMonth[0:4])+1) + '%2d'%(9-int(thisMonth[4:6]))
	months = [thisMonth, nextMonth, futureMonth, futureMonth1]
	return months

def getVIXIndex():
	#获取波动率指数
	try:
		r = requests.get("http://yunhq.sse.com.cn:32041/v1/csip/line/000188?callback=jQuery1112006556095946656515_1501032632423&select=time%2Cprice&_=1501032632431")
		j = json.loads(r.text[43:-1])
	except:
		return 0
	else:
		return j['line']

def getAtTheMoneyOption(s):
	#获取合约编号，标的代码，合约名称，寻找平值期权
	#optionDict = j['data'][0]['list'][nextMonth]['list'][c]['list'][call]
	try:
		r = s.get(starURL+"/optapi/optmktrefdata/optRefdata")
		j = json.loads(r.text)
		currentEtfPrice = getEtfCurrentPrice(s)
		a = 0
		b = 100000
		c = 0
		while a < len( j['data'][0]['list'][0]['list']):#t1
			if math.fabs(float(j['data'][0]['list'][0]['list'][a]['price']) - currentEtfPrice) < b:
				b = math.fabs(float(j['data'][0]['list'][0]['list'][a]['price']) - currentEtfPrice)
				c = a#取出平值期权
			a = a+1
		a1 = 0
		b1 = 100000
		c1 = 0
		while a1 < len( j['data'][0]['list'][1]['list']):#2
			if math.fabs(float(j['data'][0]['list'][1]['list'][a1]['price']) - currentEtfPrice) < b1:
				b1 = math.fabs(float(j['data'][0]['list'][1]['list'][a1]['price']) - currentEtfPrice)
				c1 = a1#取出平值期权
			a1 = a1+1
		a2 = 0
		b2 = 100000
		c2 = 0
		while a2 < len( j['data'][0]['list'][2]['list']):#3
			if math.fabs(float(j['data'][0]['list'][2]['list'][a2]['price']) - currentEtfPrice) < b2:
				b2 = math.fabs(float(j['data'][0]['list'][2]['list'][a2]['price']) - currentEtfPrice)
				c2 = a2#取出平值期权
			a2 = a2+1
		a3 = 0
		b3 = 100000
		c3 = 0
		while a3 < len( j['data'][0]['list'][3]['list']):#4
			if math.fabs(float(j['data'][0]['list'][3]['list'][a3]['price']) - currentEtfPrice) < b3:
				b3 = math.fabs(float(j['data'][0]['list'][3]['list'][a3]['price']) - currentEtfPrice)
				c3 = a3#取出平值期权
			a3 = a3+1
	except:
		return [-1, -1, -1, -1]
	else:
		return [c, c1, c2, c3]
#
# collectData(510050)
# collectData(510300)
# print getVIXIndex()
