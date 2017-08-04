# !/usr/bin/python
# -*- coding:utf-8 -*-
import requests,json
import collectData
import math
import utils

call = 0
put = 1
tCall = 3
tPut = 13
thisMonth = 0
nextMonth = 1
futureMonth = 2

# starURL = "https://114.55.157.119"
starURL = "https://star.sse.com.cn"

def chooseStrategy(s):
	date = time.strftime('%Y%m%d',time.localtime(time.time()))
	#PCRCall
	month = (collectData.getThisMonthAndNextMonth())[1]#次月
	dictionaryT = collectData.getOptionPriceAndStatics(month)
	a = collectData.getAtTheMoneyOption(s)#平值期权的位置　　
	call = ps['a'][a[1]][4]
	put = ps['a'][a[1]][-5]
	if call / float(put) < 3/7:
		return 0 #time to buy PCRCall
	etfDailyPrice50 = collectData.getDailyEtfPrice(510050)
	etfDailyPrice300 = collectData.getDailyEtfPrice(510300)
	trend = collectData.determineTrend(etfDailyPrice50) * collectData.determineTrend(etfDailyPrice300)
	if trend <= 1:
		#bear
		if ps['a'][a[1]][0] >= ps['a'][a[1]][-1]:
			return 1#bearCallSpread
		else:
			return 2
	elif trend >= 4:
		#bull
		if ps['a'][a[1]][0] >= ps['a'][a[1]][-1]:
			return 3#bullCallSpread
		else:
			return 4
	else:
		#波动市场
		trend = collectData.determineTrend(collectData.computeDailyVixInHistory(510050)) * collectData.determineTrend(collectData.computeDailyVixInHistory(510300))
		if trend <= 1:
			#bear
			if ps['a'][a[1]][0] + ps['a'][a[1]][-1] < 15000:
				return 5#calendarSpread
			else:
				return 6#longButterfly
		elif trend >= 4:
			#bull
			if ps['a'][a[1]][0] + ps['a'][a[1]][-1] < 15000:
				return 7#longStrangle
			else:
				return 8#longIronButterfly

def bullCallSpread(s):
	#牛市认购价差套利
	try:
		#获取合约编号，标的代码，合约名称
		r = requests.get(starURL+"/optapi/optmktrefdata/optRefdata")
		j = json.loads(r.text)
		#标的代码
		stockId = j['data'][0]['stockId']
		#买入低行权价认购合约编号，名称
		lowExercisePriceCallOptionDict = j['data'][0]['list'][nextMonth]['list'][0]['list'][call]
		lowExercisePriceCallOptionCode = lowExercisePriceCallOptionDict['code']
		lowExercisePriceCallOptionName = lowExercisePriceCallOptionDict['name']
		#卖出高行权价认购合约编号，名称
		highExercisePriceCallOptionDict = j['data'][0]['list'][nextMonth]['list'][-1]['list'][call]
		highExercisePriceCallOptionCode = highExercisePriceCallOptionDict['code']
		highExercisePriceCallOptionName = highExercisePriceCallOptionDict['name']
		#开仓
		payloadLongCall = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':lowExercisePriceCallOptionCode,  'cntrName':lowExercisePriceCallOptionName, 'orderQty':'5', 'businessType':'200', 'buySell':'B', 'optType':'C',  'coverOrUncovered':'N'}
		payloadShortCall = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':highExercisePriceCallOptionCode,  'cntrName':highExercisePriceCallOptionName, 'orderQty':'5', 'businessType':'200', 'buySell':'S', 'optType':'C',  'coverOrUncovered':'N'}
		longCall = s.post("http://star.sse.com.cn/optapi/order/apply",json = payloadLongCall)
		shortCall = s.post("http://star.sse.com.cn/optapi/order/apply",json = payloadShortCall)
		#计算止盈(损失有限)，当卖出的买权成为平值时，达到盈利极限
		upPrice = float(j['data'][0]['list'][nextMonth]['list'][-1]['price'])
		#加入待平仓序列
		month = utils.getNextMonth()
		utils.addToClosePositionList(month, j['data'][0]['list'][nextMonth]['list'][0]['price'], 0, 0,1, upPrice, 1, 0, payloadLongCall)
		utils.addToClosePositionList(month, j['data'][0]['list'][nextMonth]['list'][-1]['price'], 0, 0,1, upPrice, 1, 0, payloadShortCall)
	except:
		return 0
	else:
		return 1


def bullPutSpread(s):
	#牛市认沽价差套利
	try:
		#获取合约编号，标的代码，合约名称
		r = requests.get(starURL+"/optapi/optmktrefdata/optRefdata")
		j = json.loads(r.text)
		#标的代码
		stockId = j['data'][0]['stockId']
		#买入低行权价认沽合约编号，名称
		lowExercisePricePutOptionDict = j['data'][0]['list'][nextMonth]['list'][0]['list'][put]
		lowExercisePricePutOptionCode = lowExercisePricePutOptionDict['code']
		lowExercisePricePutOptionName = lowExercisePricePutOptionDict['name']
		print lowExercisePricePutOptionName
		#卖出高行权价认沽合约编号，名称
		highExercisePricePutOptionDict = j['data'][0]['list'][nextMonth]['list'][-1]['list'][put]
		highExercisePricePutOptionCode = highExercisePricePutOptionDict['code']
		highExercisePricePutOptionName = highExercisePricePutOptionDict['name']
		print highExercisePricePutOptionName
		#开仓
		payloadLongPut = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':lowExercisePricePutOptionCode,  'cntrName':lowExercisePricePutOptionName, 'orderQty':'5', 'businessType':'200', 'buySell':'B', 'optType':'P',  'coverOrUncovered':'N'}
		payloadShortPut = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':highExercisePricePutOptionCode,  'cntrName':highExercisePricePutOptionName, 'orderQty':'5', 'businessType':'200', 'buySell':'S', 'optType':'P',  'coverOrUncovered':'N'}
		longPut = s.post("http://star.sse.com.cn/optapi/order/apply",json = payloadLongPut)
		shortPut = s.post("http://star.sse.com.cn/optapi/order/apply",json = payloadShortPut)
		#计算止盈(损失有限)，当卖出的卖权成为平值时，达到盈利极限
		upPrice = float(j['data'][0]['list'][nextMonth]['list'][-1]['price'])
		#加入待平仓序列
		month = utils.getNextMonth()
		utils.addToClosePositionList(month, j['data'][0]['list'][nextMonth]['list'][0]['price'], 0, 0, 1, upPrice, 1, 0, payloadLongCall)
		utils.addToClosePositionList(month, j['data'][0]['list'][nextMonth]['list'][-1]['price'], 0, 0, 1, upPrice, 1, 0, payloadShortCall)
	except:
		return 0
	else:
		return 1

def bearCallSpread(s):
	#熊市认购价差套利
	try:
		#获取合约编号，标的代码，合约名称
		r = requests.get(starURL+"/optapi/optmktrefdata/optRefdata")
		j = json.loads(r.text)
		#标的代码
		stockId = j['data'][0]['stockId']
		#卖出低行权价认购合约编号，名称
		lowExercisePriceCallOptionDict = j['data'][0]['list'][nextMonth]['list'][0]['list'][call]
		lowExercisePriceCallOptionCode = lowExercisePriceCallOptionDict['code']
		lowExercisePriceCallOptionName = lowExercisePriceCallOptionDict['name']
		#买入高行权价认购合约编号，名称
		highExercisePriceCallOptionDict = j['data'][0]['list'][nextMonth]['list'][-1]['list'][call]
		highExercisePriceCallOptionCode = highExercisePriceCallOptionDict['code']
		highExercisePriceCallOptionName = highExercisePriceCallOptionDict['name']
		#开仓
		payloadShortCall = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':lowExercisePriceCallOptionCode,  'cntrName':lowExercisePriceCallOptionName, 'orderQty':'5', 'businessType':'200', 'buySell':'S', 'optType':'C',  'coverOrUncovered':'N'}
		payloadLongCall = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':highExercisePriceCallOptionCode,  'cntrName':highExercisePriceCallOptionName, 'orderQty':'5', 'businessType':'200', 'buySell':'B', 'optType':'C',  'coverOrUncovered':'N'}
		longCall = s.post("http://star.sse.com.cn/optapi/order/apply",json = payloadLongCall)
		shortCall = s.post("http://star.sse.com.cn/optapi/order/apply",json = payloadShortCall)
		#计算止盈，当卖出的买权成为平值时，达到盈利极限
		downPrice = float(j['data'][0]['list'][nextMonth]['list'][0]['price'])
		#加入待平仓序列
		month = utils.getNextMonth()
		utils.addToClosePositionList(month, j['data'][0]['list'][nextMonth]['list'][0]['price'], 0, 0, 0, downPrice, 1, 100000, payloadShortCall)
		utils.addToClosePositionList(month, j['data'][0]['list'][nextMonth]['list'][-1]['price'], 0, 0, 0, downPrice, 1, 100000, payloadLongCall)
	except:
		return 0
	else:
		return 1

def bearPutSpread(s):
	#熊市认沽套利
	try:
		#获取合约编号，标的代码，合约名称
		r = requests.get(starURL+"/optapi/optmktrefdata/optRefdata")
		j = json.loads(r.text)
		#标的代码
		stockId = j['data'][0]['stockId']
		#卖出低行权价认沽合约编号，名称
		lowExercisePricePutOptionDict = j['data'][0]['list'][nextMonth]['list'][0]['list'][put]
		lowExercisePricePutOptionCode = lowExercisePricePutOptionDict['code']
		lowExercisePricePutOptionName = lowExercisePricePutOptionDict['name']
		#买入高行权价认沽合约编号，名称
		highExercisePricePutOptionDict = j['data'][0]['list'][nextMonth]['list'][-1]['list'][put]
		highExercisePricePutOptionCode = highExercisePricePutOptionDict['code']
		highExercisePricePutOptionName = highExercisePricePutOptionDict['name']
		#开仓
		payloadShortPut = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':lowExercisePricePutOptionCode,  'cntrName':lowExercisePricePutOptionName, 'orderQty':'5', 'businessType':'200', 'buySell':'S', 'optType':'P',  'coverOrUncovered':'N'}
		payloadLongPut = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':highExercisePricePutOptionCode,  'cntrName':highExercisePricePutOptionName, 'orderQty':'5', 'businessType':'200', 'buySell':'B', 'optType':'P',  'coverOrUncovered':'N'}
		longCall = s.post("http://star.sse.com.cn/optapi/order/apply",json = payloadLongPut)
		shortCall = s.post("http://star.sse.com.cn/optapi/order/apply",json = payloadShortPut)
		#计算止盈，当卖出的卖权成为平值时，达到盈利极限
		downPrice = float(j['data'][0]['list'][nextMonth]['list'][0]['price'])
		#加入待平仓序列
		month = utils.getNextMonth()
		utils.addToClosePositionList(month, j['data'][0]['list'][nextMonth]['list'][0]['price'], 0, 0, 0, downPrice, 1, 100000, payloadShortCall)
		utils.addToClosePositionList(month, j['data'][0]['list'][nextMonth]['list'][-1]['price'], 0, 0, 0, downPrice, 1, 100000, payloadLongCall)
	except:
		return 0
	else:
		return 1

def calendarSpread(s):
	#日历套利
	try:
		#获取合约编号，标的代码，合约名称
		r = s.get(starURL+"/optapi/optmktrefdata/optRefdata")
		j = json.loads(r.text)
		print r.text
		#标的代码
		stockId = j['data'][0]['stockId']
		#自动检索平值期权在list中的位置，注意不同月份的行权价格数不同
		a = collectData.getAtTheMoneyOption(s)
		#卖出近期认购合约编号，名称
		currentOptionDict = j['data'][0]['list'][thisMonth]['list'][a[0]]['list'][call]
		currentOptionCode = currentOptionDict['code']
		currentOptionName = currentOptionDict['name']
		#买入远期认购合约编号，名称
		futureOptionDict = j['data'][0]['list'][futureMonth]['list'][a[2]]['list'][call]
		futureOptionCode = futureOptionDict['code']
		futureOptionName = futureOptionDict['name']
		print stockId
		print currentOptionCode,futureOptionCode
		print currentOptionName,futureOptionName
		#开仓
		payloadLongCall = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':futureOptionCode,  'cntrName':futureOptionName, 'orderQty':'5', 'businessType':'200', 'buySell':'B', 'optType':'C',  'coverOrUncovered':'N'}
		payloadShortCall = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':currentOptionCode,  'cntrName':currentOptionName, 'orderQty':'5', 'businessType':'200', 'buySell':'S', 'optType':'C',  'coverOrUncovered':'N'}
		rLongCall = s.post(starURL+"/optapi/order/apply",json = payloadLongCall)
		rShortCall = s.post(starURL+"/optapi/order/apply",json = payloadShortCall)
		#近期合约到期即平仓，无需止盈止损
		#加入待平仓序列
		month1 = (collectData.getThisMonthAndNextMonth())[0]
		month2 = (collectData.getThisMonthAndNextMonth())[2]
		utils.addToClosePositionList(month1, j['data'][0]['list'][thisMonth]['list'][a[0]]['price'], 3, 0, 0, 0, 0, 0, payloadShortCall)
		utils.addToClosePositionList(month2, j['data'][0]['list'][futureMonth]['list'][a[2]]['price'], 3, 0, 0, 0, 0, 0, payloadLongCall)
	except:
		return 0
	else:
		return 1

def longButterfly(s):
	try:
		#获取合约编号，标的代码，合约名称
		r = s.get(starURL+"/optapi/optmktrefdata/optRefdata")
		j = json.loads(r.text)
		month2 = (collectData.getThisMonthAndNextMonth())[1]

		#标的代码
		stockId = j['data'][0]['stockId']
		#自动检索平值期权在list中的位置，注意不同月份的行权价格数不同
		a = collectData.getAtTheMoneyOption(s)
		#获取T型报价中各个期权的价格
		ps = collectData.getOptionPriceAndStatics(int(month2))
		op1 = ps['a'][0][tCall]
		op2 = ps['a'][a[1]][tCall]
		op3 = ps['a'][-1][tCall]
		opx1 = j['data'][0]['list'][nextMonth]['list'][0]['price']
		opx2 = j['data'][0]['list'][nextMonth]['list'][a[1]]['price']
		opx3 = j['data'][0]['list'][nextMonth]['list'][-1]['price']

		#买入认购合约编号，名称
		currentOptionDict = j['data'][0]['list'][nextMonth]['list'][0]['list'][call]
		currentOptionCode = currentOptionDict['code']
		currentOptionName = currentOptionDict['name']
		print currentOptionName
		#卖出两份认购合约编号，名称
		mediumOptionDict = j['data'][0]['list'][nextMonth]['list'][a[1]]['list'][call]
		mediumOptionCode = mediumOptionDict['code']
		mediumOptionName = mediumOptionDict['name']
		print mediumOptionName
		#买入认购合约编号，名称
		futureOptionDict = j['data'][0]['list'][nextMonth]['list'][-1]['list'][call]
		futureOptionCode = futureOptionDict['code']
		futureOptionName = futureOptionDict['name']
		print futureOptionName
		#开仓
		payloadLongCall1 = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':currentOptionCode,  'cntrName':currentOptionName, 'orderQty':'2', 'businessType':'200', 'buySell':'B', 'optType':'C',  'coverOrUncovered':'N'}
		payloadShortCall2 = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':mediumOptionCode,  'cntrName':mediumOptionName, 'orderQty':'4', 'businessType':'200', 'buySell':'S', 'optType':'C',  'coverOrUncovered':'N'}
		payloadLongCall3 = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':futureOptionCode,  'cntrName':futureOptionName, 'orderQty':'2', 'businessType':'200', 'buySell':'B', 'optType':'C',  'coverOrUncovered':'N'}
		longCall1 = s.post(starURL+"/optapi/order/apply",json = payloadLongCall1)
		longCall2 = s.post(starURL+"/optapi/order/apply",json = payloadShortCall2)
		longCall3 = s.post(starURL+"/optapi/order/apply",json = payloadLongCall3)
		#待完成：判断平仓条件
		pointPrice = opx2#在卖出的认购期权恰好为平值时，达到盈利的顶点　
		lostPoint = -0.1#设置止损
		downPrice = opx1 + (lostPoint + 1) * (op1 + op3 - 2 * op2)
		upPrice =  (2 * opx2 - opx1) - (lostPoint + 1) * (op1 + op3 - 2 * op2)

		#加入待平仓序列
		#止盈
		utils.addToClosePositionList(month2, j['data'][0]['list'][nextMonth]['list'][0]['price'], 0, 0, 2,pointPrice, 2, pointPrice,  payloadLongCall1)
		utils.addToClosePositionList(month2, j['data'][0]['list'][nextMonth]['list'][a[1]]['price'], 0, 0, 2,pointPrice, 2, pointPrice, payloadShortCall2)
		utils.addToClosePositionList(month2, j['data'][0]['list'][nextMonth]['list'][-1]['price'], 0, 0, 2,pointPrice, 2, pointPrice, payloadLongCall3)
		#止损
		utils.addToClosePositionList(month2, j['data'][0]['list'][nextMonth]['list'][0]['price'], 0, 0, 0,downPrice, 1, upPrice,  payloadLongCall1)
		utils.addToClosePositionList(month2, j['data'][0]['list'][nextMonth]['list'][a[1]]['price'], 0, 0, 0,downPrice, 1, upPrice, payloadShortCall2)
		utils.addToClosePositionList(month2, j['data'][0]['list'][nextMonth]['list'][-1]['price'], 0, 0, 0,downPrice, 1, upPrice, payloadLongCall3)
	except:
		return 0
	else:
		return 1

def longStrangle(s):
	#买入宽跨式套利
	try:
		#获取合约编号，标的代码，合约名称
		r = requests.get(starURL+"/optapi/optmktrefdata/optRefdata")
		j = json.loads(r.text)
		#标的代码
		stockId = j['data'][0]['stockId']
		#买入低行权价认沽合约编号，名称
		lowExercisePricePutOptionDict = j['data'][0]['list'][nextMonth]['list'][0]['list'][put]
		lowExercisePricePutOptionCode = lowExercisePricePutOptionDict['code']
		lowExercisePricePutOptionName = lowExercisePricePutOptionDict['name']
		#买入高行权价认购合约编号，名称
		highExercisePriceCallOptionDict = j['data'][0]['list'][nextMonth]['list'][-1]['list'][call]
		highExercisePriceCallOptionCode = highExercisePriceCallOptionDict['code']
		highExercisePriceCallOptionName = highExercisePriceCallOptionDict['name']
		#开仓
		payloadLongPut = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':lowExercisePricePutOptionCode,  'cntrName':lowExercisePricePutOptionName, 'orderQty':'5', 'businessType':'200', 'buySell':'B', 'optType':'P',  'coverOrUncovered':'N'}
		payloadLongCall = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':highExercisePriceCallOptionCode,  'cntrName':highExercisePriceCallOptionName, 'orderQty':'5', 'businessType':'200', 'buySell':'B', 'optType':'C',  'coverOrUncovered':'N'}
		longPut = s.post("http://star.sse.com.cn/optapi/order/apply",json = payloadLongPut)
		longCall = s.post("http://star.sse.com.cn/optapi/order/apply",json = payloadLongCall)

		#加入待平仓序列
		month = utils.getNextMonth()
		utils.addToClosePositionList(month, j['data'][0]['list'][nextMonth]['list'][0]['price'], 0, 0, payloadLongPut)
		utils.addToClosePositionList(month, j['data'][0]['list'][nextMonth]['list'][-1]['price'], 0, 0, payloadLongCall)
	except:
		return 0
	else:
		return 1

def longIronButterfly(s):
	#买入铁蝴蝶式套利
	try:
		#获取合约编号，标的代码，合约名称
		r = s.get(starURL+"/optapi/optmktrefdata/optRefdata")
		j = json.loads(r.text)
		#标的代码
		stockId = j['data'][0]['stockId']
		#自动检索平值期权在list中的位置，注意不同月份的行权价格数不同
		a = collectData.getAtTheMoneyOption(s)
		#
		optionDict = j['data'][0]['list'][nextMonth]['list'][0]['list'][put]
		optionCode = optionDict['code']
		optionName = optionDict['name']
		optionDict1 = j['data'][0]['list'][nextMonth]['list'][a[1]]['list'][put]
		optionCode1 = optionDict1['code']
		optionName1 = optionDict1['name']
		optionDict2 = j['data'][0]['list'][nextMonth]['list'][a[1]]['list'][call]
		optionCode2 = optionDict2['code']
		optionName2 = optionDict2['name']
		optionDict3 = j['data'][0]['list'][nextMonth]['list'][-1]['list'][call]
		optionCode3 = optionDict3['code']
		optionName3 = optionDict3['name']

		#开仓
		payloadShortPut1 = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':optionCode,  'cntrName':optionName, 'orderQty':'5', 'businessType':'200', 'buySell':'S', 'optType':'P',  'coverOrUncovered':'N'}
		payloadLongPut2 = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':optionCode1,  'cntrName':optionName1, 'orderQty':'5', 'businessType':'200', 'buySell':'B', 'optType':'P',  'coverOrUncovered':'N'}
		payloadLongCall3 = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':optionCode2,  'cntrName':optionName2, 'orderQty':'5', 'businessType':'200', 'buySell':'B', 'optType':'C',  'coverOrUncovered':'N'}
		payloadShortCall4 = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':optionCode3,  'cntrName':optionName3, 'orderQty':'5', 'businessType':'200', 'buySell':'S', 'optType':'C',  'coverOrUncovered':'N'}

		shortPut1 = s.post(starURL+"/optapi/order/apply",json = payloadShortPut1)
		longPut2 = s.post(starURL+"/optapi/order/apply",json = payloadLongPut2)
		longCall3 = s.post(starURL+"/optapi/order/apply",json = payloadLongCall3)
		shortCall4 = s.post(starURL+"/optapi/order/apply",json = payloadShortCall4)

		#待完成：判断平仓条件
		#加入待平仓序列
		month1 = (collectData.getThisMonthAndNextMonth())[0]
		month2 = (collectData.getThisMonthAndNextMonth())[1]
		month3 = (collectData.getThisMonthAndNextMonth())[2]
		month4 = (collectData.getThisMonthAndNextMonth())[3]

		utils.addToClosePositionList(month1, j['data'][0]['list'][nextMonth]['list'][0]['price'], 0, 0, 0,  j['data'][0]['list'][nextMonth]['list'][0]['price'], 1, j['data'][0]['list'][nextMonth]['list'][-1]['price'],  payloadShortPut1)
		utils.addToClosePositionList(month2, j['data'][0]['list'][nextMonth]['list'][0]['price'], 0, 0, 0,  j['data'][0]['list'][nextMonth]['list'][0]['price'], 1, j['data'][0]['list'][nextMonth]['list'][-1]['price'],  payloadLongPut2)
		utils.addToClosePositionList(month3, j['data'][0]['list'][nextMonth]['list'][0]['price'], 0, 0, 0,  j['data'][0]['list'][nextMonth]['list'][0]['price'], 1, j['data'][0]['list'][nextMonth]['list'][-1]['price'],  payloadLongCall3)
		utils.addToClosePositionList(month4, j['data'][0]['list'][nextMonth]['list'][0]['price'], 0, 0, 0,  j['data'][0]['list'][nextMonth]['list'][0]['price'], 1, j['data'][0]['list'][nextMonth]['list'][-1]['price'],  payloadShortCall4)
	except:
		return 0
	else:
		return 1

def PCRCall(s):
	#PCR投机
	try:
		#获取合约编号，标的代码，合约名称，寻找平值期权
		r = s.get(starURL+"/optapi/optmktrefdata/optRefdata")
		j = json.loads(r.text)
		#寻找平值期权位置
		month = 201707
		optData = collectData.getOptionPriceAndStatics(month)
		currentEtfPrice = collectData.getEtfCurrentPrice(s)
		a = 0
		b = 100000
		c = 0
		while a < len( j['data'][0]['list'][nextMonth]['list']):
			if math.fabs(float(j['data'][0]['list'][nextMonth]['list'][a]['price']) - currentEtfPrice) < b:
				b = math.fabs(float(j['data'][0]['list'][nextMonth]['list'][a]['price']) - currentEtfPrice)
				c = a#取出平值期权
			a = a+1
		stockId = j['data'][0]['stockId']
		optionDict = j['data'][0]['list'][nextMonth]['list'][c]['list'][call]
		optionCode = optionDict['code']
		optionName = optionDict['name']
		#开仓
		payloadCall = {'uStockCode':stockId,'posEffect':'O','orderType':'M','cntrCode':optionCode,  'cntrName':optionName, 'orderQty':'5', 'businessType':'200', 'buySell':'B', 'optType':'C',  'coverOrUncovered':'N'}
		Call = s.post("http://star.sse.com.cn/optapi/order/apply",json = payloadCall)
		#计算止盈止损
		currentPrice = float(optData['a'][c][7])
		downPrice = currentPrice * 0.96
		upPrice = currentPrice * 1.1

		#加入待平仓序列
		utils.addToClosePositionList(month, j['data'][0]['list'][nextMonth]['list'][c]['price'], 0, 0, 0, downPrice, 1, upPrice, payloadCall)
	except:
		return 0
	else:
		return 1
