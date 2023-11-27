import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from helpers import generateForecast, generatePlotHistoric, getOrder

import matplotlib
matplotlib.use('agg')
import pandas as pd



# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


cluster = pd.read_csv("static/out.csv")
preds =pd.read_csv("static/preds.csv")

countries = pd.unique(preds["Entity"])
indicators = list(preds.columns)
indicators.remove("Year")
indicators.remove("Entity")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET"])
def index():
    missing_countries= ["Bermuda", "Bulgaria","Aruba", "Albania", "Puerto Rico","New Caledonia", "Libya", "Lebanon", "French Guiana", "Cayman Islands"]
    missing_countries=sorted(missing_countries)
    last = missing_countries[-1]
    return render_template("index.html", missing=missing_countries, last=last)

@app.route("/clusters", methods=["GET"])
def clusters():
    countrylist = ["Antigua and Barbuda", "Bahrain", "Barbados", "Comoros", "Congo", "Grenada", "Kiribati", "Maldives", "Malta",
                   "Mauritius", "Nauru", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa",
                   "Sao Tome and Principe", "Seychelles", "Singapore", "Tonga", "Tuvalu"]

    last=countrylist[-1]
    cluster1 = cluster[cluster["Labels"]==0]
    cl1last = cluster1["Entity"].iloc[-1]
    len1 = len(cluster1)
    cluster2 = cluster[cluster["Labels"]==1]
    cl2last = cluster2["Entity"].iloc[-1]
    len2 = len(cluster2)
    cluster3 = cluster[cluster["Labels"]==2]
    cl3last = cluster3["Entity"].iloc[-1]
    len3 = len(cluster3)

    means1=cluster1.drop(columns='Entity')
    means1 = means1.mean()

    means2=cluster2.drop(columns='Entity')
    means2 = means2.mean()

    means3=cluster3.drop(columns='Entity')
    means3 = means3.mean()

    means1=means1.to_frame()
    means1=means1.drop(index="Labels")
    means1=means1.to_html(header=False)

    means2=means2.to_frame()
    means2=means2.drop(index="Labels")
    means2=means2.to_html(header=False)

    means3=means3.to_frame()
    means3=means3.drop(index="Labels")
    means3=means3.to_html(header=False)

    return render_template("clusters.html", missing=countrylist, last=last, cluster1=cluster1,
    cluster2=cluster2, cl1last=cl1last, cl2last=cl2last, len1=len1, len2=len2, means1=means1, means2=means2,
    cluster3=cluster3, cl3last=cl3last, len3=len3, means3=means3)



@app.route("/preds", methods=["GET", "POST"])
def predictions():
    errormsg = "no"


    if request.method=="POST":
        if request.form.get("country")=="Select country here":
            errormsg="empty"
            return render_template("preds.html", countries=countries,
                            indicators=indicators, errormsg=errormsg, plt1=None, plt2=None)
        if request.form.get("indicator")=="Select indicator here":
            errormsg="empty"
            return render_template("preds.html", countries=countries,
                            indicators=indicators, errormsg=errormsg, plt1=None, plt2=None)


        country = request.form.get("country")
        ind = request.form.get("indicator")

        if ind == "Access to electricity (% of population)":
            order = (5,3,0)

        elif ind == "Access to clean fuels for cooking":
            order = (0,1,0)

        elif ind == "Renewable energy share in the total final energy consumption (%)":
            order = (4,1,4)
        elif ind == "Energy intensity level of primary energy (MJ/$2017 PPP GDP)":
            order = (0,1,0)
        else:
            errormsg = "yes"
            return render_template("preds.html", countries=countries,
                    indicators=indicators, errormsg=errormsg, plt1=None, plt2=None)
        order = getOrder(preds, ind, country)
        print(order)
        plot1 = generatePlotHistoric(preds, ind, country)
        plot2=generateForecast(preds, ind, country, order)


        return render_template("preds.html", countries=countries,
                               indicators=indicators, errormsg=errormsg,plt1 = plot1, plt2=plot2)


    else:
        return render_template("preds.html", countries=countries,
                               indicators=indicators, errormsg=errormsg, plt1=None, plt2=None)