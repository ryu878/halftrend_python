# Ryuryu's HalfTrend Indicator Python Fork
# Original pine script code: https://www.tradingview.com/script/U1SJ8ubc-HalfTrend/
# -------------------------------------
# (c) 2023 Ryan Hayabusa 
# Github: https://github.com/ryu878 
# Web: https://aadresearch.xyz/
# Discord: ryuryu#4087
# -------------------------------------

'''
Original tradingview pine script code:
https://www.tradingview.com/script/U1SJ8ubc-HalfTrend/
'''

'''
//@version=4
// Copyright (c) 2021-present, Alex Orekhov (everget)
study("HalfTrend", overlay=true)

amplitude = input(title="Amplitude", defval=2)
channelDeviation = input(title="Channel Deviation", defval=2)
showArrows = input(title="Show Arrows", defval=true)
showChannels = input(title="Show Channels", defval=true)

var int trend = 0
var int nextTrend = 0
var float maxLowPrice = nz(low[1], low)
var float minHighPrice = nz(high[1], high)

var float up = 0.0
var float down = 0.0
float atrHigh = 0.0
float atrLow = 0.0
float arrowUp = na
float arrowDown = na

atr2 = atr(100) / 2
dev = channelDeviation * atr2

highPrice = high[abs(highestbars(amplitude))]
lowPrice = low[abs(lowestbars(amplitude))]
highma = sma(high, amplitude)
lowma = sma(low, amplitude)

if nextTrend == 1
	maxLowPrice := max(lowPrice, maxLowPrice)

	if highma < maxLowPrice and close < nz(low[1], low)
		trend := 1
		nextTrend := 0
		minHighPrice := highPrice
else
	minHighPrice := min(highPrice, minHighPrice)

	if lowma > minHighPrice and close > nz(high[1], high)
		trend := 0
		nextTrend := 1
		maxLowPrice := lowPrice

if trend == 0
	if not na(trend[1]) and trend[1] != 0
		up := na(down[1]) ? down : down[1]
		arrowUp := up - atr2
	else
		up := na(up[1]) ? maxLowPrice : max(maxLowPrice, up[1])
	atrHigh := up + dev
	atrLow := up - dev
else
	if not na(trend[1]) and trend[1] != 1 
		down := na(up[1]) ? up : up[1]
		arrowDown := down + atr2
	else
		down := na(down[1]) ? minHighPrice : min(minHighPrice, down[1])
	atrHigh := down + dev
	atrLow := down - dev

ht = trend == 0 ? up : down

var color buyColor = color.blue
var color sellColor = color.red

htColor = trend == 0 ? buyColor : sellColor
htPlot = plot(ht, title="HalfTrend", linewidth=2, color=htColor)

atrHighPlot = plot(showChannels ? atrHigh : na, title="ATR High", style=plot.style_circles, color=sellColor)
atrLowPlot = plot(showChannels ? atrLow : na, title="ATR Low", style=plot.style_circles, color=buyColor)

fill(htPlot, atrHighPlot, title="ATR High Ribbon", color=sellColor)
fill(htPlot, atrLowPlot, title="ATR Low Ribbon", color=buyColor)

buySignal = not na(arrowUp) and (trend == 0 and trend[1] == 1)
sellSignal = not na(arrowDown) and (trend == 1 and trend[1] == 0)

plotshape(showArrows and buySignal ? atrLow : na, title="Arrow Up", style=shape.triangleup, location=location.absolute, size=size.tiny, color=buyColor)
plotshape(showArrows and sellSignal ? atrHigh : na, title="Arrow Down", style=shape.triangledown, location=location.absolute, size=size.tiny, color=sellColor)

alertcondition(buySignal, title="Alert: HalfTrend Buy", message="HalfTrend Buy")
alertcondition(sellSignal, title="Alert: HalfTrend Sell", message="HalfTrend Sell")


'''

import pandas as pd
import pandas_ta as ta
from config import *


# Create nz and na logic from pine script
def nz(value, default):
    return default if pd.isnull(value) else value


def na(value):
    return pd.isnull(value)

# Read the data from sample file
data = pd.read_csv('sample_data.csv')
df = pd.DataFrame(data)
df = df.reset_index()

# Convert float columns to Python float
df['open'] = df['open'].astype(float).apply(float)
df['high'] = df['high'].astype(float).apply(float)
df['low'] = df['low'].astype(float).apply(float)
df['close'] = df['close'].astype(float).apply(float)

# HalfTrend
out = []
trend = 0
nextTrend = 0
up = 0.0
down = 0.0
atrHigh = 0.0
atrLow = 0.0
direction = None

atr_N = ta.atr(df['high'], df['low'], df['close'], window=atrlen)
highma_N = ta.sma(df['high'], amplitude)
lowma_N = ta.sma(df['low'], amplitude)
highestbars = df['high'].rolling(amplitude, min_periods=1).max()
lowestbars = df['low'].rolling(amplitude, min_periods=1).min()
df['highestbars'] = highestbars
df['lowestbars'] = lowestbars

arrTrend = [None] * len(df)
arrUp = [None] * len(df)
arrDown = [None] * len(df)

maxLowPrice = df['low'].iat[atrlen - 1]
minHighPrice = df['high'].iat[atrlen - 1]

if df['close'].iat[0] > df['low'].iat[atrlen]:
    trend = 1
    nextTrend = 1

for i in range(1, len(df)):
    atr2 = atr_N.iat[i] / 2.0
    dev = channel_deviation * atr2

    highPrice = highestbars.iat[i]
    lowPrice = lowestbars.iat[i]

    if nextTrend == 1:
        maxLowPrice = max(lowPrice, maxLowPrice)
        if highma_N.iat[i] < maxLowPrice and df['close'].iat[i] < nz(df['low'].iat[i - 1], df['low'].iat[i]):
            trend = 1
            nextTrend = 0
            minHighPrice = highPrice
    else:
        minHighPrice = min(highPrice, minHighPrice)
        if lowma_N.iat[i] > minHighPrice and df['close'].iat[i] > nz(df['high'].iat[i - 1], df['high'].iat[i]):
            trend = 0
            nextTrend = 1
            maxLowPrice = lowPrice
    arrTrend[i] = trend

    if trend == 0:
        if not na(arrTrend[i - 1]) and arrTrend[i - 1] != 0:
            up = down if na(arrDown[i - 1]) else arrDown[i - 1]
        else:
            up = maxLowPrice if na(arrUp[i - 1]) else max(maxLowPrice, arrUp[i - 1])
        direction = 'long'
        atrHigh = up + dev
        atrLow = up - dev
        arrUp[i] = up
    else:
        if not na(arrTrend[i - 1]) and arrTrend[i - 1] != 1:
            down = up if na(arrUp[i - 1]) else arrUp[i - 1]
        else:
            down = minHighPrice if na(arrDown[i - 1]) else min(minHighPrice, arrDown[i - 1])
        direction = 'short'
        atrHigh = down + dev
        atrLow = down - dev
        arrDown[i] = down

    if trend == 0:
        out.append([atrHigh, up, atrLow, direction, arrUp[i], arrDown[i]])
    else:
        out.append([atrHigh, down, atrLow, direction, arrUp[i], arrDown[i]])

df = pd.DataFrame(out, columns=['atrHigh', 'close', 'atrLow', 'direction', 'arrUp', 'arrDown'])

print(df)
