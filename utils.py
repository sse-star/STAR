# !/usr/bin/python
# -*- coding:utf-8 -*-
import requests,json

# starURL = "https://114.55.157.119"
starURL = "http://star.sse.com.cn"


def logIn(username, password):
	#登陆star系统
	s = requests.session()
	login_data = {'username':username,'password':password}
	try:
		r = s.post(starURL+"/lgnapi/login", login_data)
	except:
		return 'error'
	else:
		return s

def logOut(s):
	#登出
	try:
		r = s.post(starURL+"/lgnapi/logout")
	except:
		return 'error'
	else:
		return json.loads(r.text)['status']

def isLogIn(s):
	#判断是否成功登陆
	try:
		r = s.get(starURL+"/isLogin")
	except:
		return 'error'
	else:
		return json.loads(r.text)['status']

def loadJson(fileName):
	f = open("/Users/bill/Documents/intern_sseTech/test/%s" % fileName)
	# f.encoding = 'utf-8'
	j = json.load(f)
	payload = j['payload']
	return payload

def addToClosePositionList(month, exercisePrice, etfOrCallOrPutOrMonth, sign, sign1, price1, sign2, price2, data):
	#月份，行权价，ETF/call/put/month, or/and，</>/=，价格1, </>/=，价格2, 数据包
	try:
		f = open("/Users/bill/Documents/intern_sseTech/test/%d_%s_%d_%d_%d_%f_%d_%f.json"%(int(month), exercisePrice, etfOrCallOrPutOrMonth,sign, sign1, price1, sign2, price2), 'wb')
		f.write(json.dumps(data))
		f.close
	except:
		return 0
	else:
		return 1

def getNextMonth():
	return 201708

def determineWhetherClosePosition(p, sign, sign1, price1, sign2, price2):
	if sign == 0:
		#or
		if sign1 == 0:
			if p < price1:
				return 1
		elif sign1 == 1:
			if p > price1:
				return 1
		else:
			if p == price1:
				return 1
	else:
		if sign1 == 1 and sign2 == 0:
			if p > price1 and p < price2:
				return 1

def closePosition(s, fil):
	try:
		p = loadJson( fil)
		pl = p['payload']
		if pl['buySell'] == 'B':
			pl['buySell'] = 'S'
		else:
			pl['buySell'] = 'B'
		if pl['posEffect'] == 'O':
			pl['posEffect'] = 'C'
		closePositionResponse = s.post("http://star.sse.com.cn/optapi/order/apply",json = pl)
		#清除带平仓序列
		# os.remove(fil)
	except:
		return 0
	else:
		return 1
