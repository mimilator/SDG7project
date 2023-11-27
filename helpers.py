import csv
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from io import BytesIO
import base64
import pandas as pd
import pmdarima as pm
import numpy as np

fontsize = 16

def replaceValue(value):
    if value>100:
        value=100
        return value
    elif value<0:
        value = 0
        return value
    else:
        return value

def generateForecast(data, topred, country, order):
    subset = data.loc[data['Entity']== country,[topred, 'Year']]
    subset.index=subset['Year']
    subset=subset.drop(columns="Year")
    train = subset[subset.index <= 2021]
    y=train[topred]
    ARIMAmodel = ARIMA(y, order=order).fit()
    preds = ARIMAmodel.get_forecast(10)

    predsdf = preds.conf_int(alpha=0.05)
    predsdf["Predictions"] = ARIMAmodel.predict(start = predsdf.index[0], end = predsdf.index[-1])
    predsdf.index = range(2021,2031)
    if predsdf["Predictions"].max()>100 or predsdf["Predictions"].min()<0:
        predsdf["Predictions"]=predsdf["Predictions"].apply(replaceValue)

    print(predsdf["Predictions"])

    fig, ax = plt.subplots(figsize=(11,8))

    ax.plot(predsdf["Predictions"], color ="Yellow", label="ARIMA Model Predictions", linewidth=6)
    ax.set_ylabel(topred, fontsize = fontsize)
    ax.set_xlabel("Year", fontsize = fontsize)
    ax.set_xticks(range(2020,2031,5))
    ax.set_yticks(np.arange(0, data[topred].max()+10, data[topred].max()/10))


    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_title(f"Predictions until 2030 for {country}", fontsize = fontsize+3, pad=20)
    ax.legend()

    img_buf=BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
    plt.close()



    return img_base64

def generatePlotHistoric(data, topred, country):
    subset = data.loc[data['Entity']== country,[topred, 'Year']]
    subset.index=subset['Year']
    subset=subset.drop(columns="Year")


    fig, ax = plt.subplots(figsize=(10,8))
    ax.plot(subset, color="black", label="Observed data")
    ax.set_ylabel(topred, fontsize = fontsize)
    ax.set_xlabel("Year", fontsize = fontsize)
    ax.set_xticks(range(2000,2021,5))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_yticks(np.arange(0, data[topred].max()+1, data[topred].max()/10))
    ax.set_title(f"Data on {topred} \n for {country} \n for 2000-2020", fontsize = fontsize + 3, pad=10)
    ax.legend()
    img_buf=BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
    plt.close()



    return img_base64

def getOrder(data, var, country):
    try:
        subset = data.loc[data['Entity']== country,[var, 'Year']]
        subset.index=subset['Year']
        subset=subset.drop(columns="Year")
        train = subset[subset.index <= 2021]

        model = pm.auto_arima(train, start_p=1, start_q=1,
                           test='adf',
                           max_p=20, max_q=20, d_max=3,
                           m=1,
                           d=None,
                           seasonal=False,  
                           trace=True,
                           suppress_warnings=True)
        return model.order

    except:
        order=(1,1,1)
        return order
