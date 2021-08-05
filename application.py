import os
from flask import Flask, flash, redirect, render_template, request
import numpy as np
import math
from scipy.optimize import fsolve
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

# Configure application
app = Flask(__name__)

# usd formatting. Credit to CS50x's finance pset
def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

# Custom filter
app.jinja_env.filters["usd"] = usd

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# equation function that will be evaluated to determine time until retirement with fsolve
def equation(time, *equation_inputs):
    # unpack equation_inputs
    retirement_nest_egg, stocks, bonds, annual_stock_contribution, annual_bond_contribution, stockinterest, bondinterest = equation_inputs
    expression = ((stocks + annual_stock_contribution) * (1 + stockinterest / 100)**time) + ((bonds + annual_bond_contribution) * (1 + bondinterest / 100)**time)
    return (retirement_nest_egg - (expression))

def invested_networth(time,stocks, bonds, annual_stock_contribution, annual_bond_contribution, stockinterest, bondinterest):
    invested_net_worth = ((stocks + annual_stock_contribution) * (1 + stockinterest / 100)**time) + ((bonds + annual_bond_contribution) * (1 + bondinterest / 100)**time)
    return invested_net_worth


def form_input_checking():
    # get all text inputs from form
    currentage = request.form.get("Age")
    income = request.form.get("Annual_post-tax_income")
    monthlycurrexpenses = request.form.get("Monthly_Expenses")
    stocks = request.form.get("Stocks")
    bonds = request.form.get("Bonds")
    cash = request.form.get("Cash")
    debt = request.form.get("Debt")
    monthlyretireexpenses = request.form.get("retirementexpenses")

    textinputs = [currentage, income, monthlycurrexpenses, stocks, bonds, cash, debt, monthlyretireexpenses]
    numericinputs =[]

    # remove $, "," characters from text input
    for textinput in textinputs:
        textinput=textinput.strip()
        textinput=textinput.replace(',','')
        textinput=textinput.replace('$','')

        # check if textinput is empty after removing ',' and '$'
        if textinput =='':
            return 0
        # return error if text inputs have alpha characters
        if textinput.isalpha():
            return 0
        # return error if a negative sign in inputs;
        if "-" in textinput:
            return 0

        #check for symbols
        symbols = "!@#%^&*()_-+={}[]"

        for char in textinput:
            if char in symbols:
                return 0

        #return error if inputs are negative
        if float(textinput) < 0:
            return 0

        numericinputs.append(float(textinput))
    return numericinputs


@app.route("/", methods = ["POST", "GET"])
def index():

    if request.method == "GET":
        return render_template("index.html")
    else:
        # run input error checking function
        floatinputs = form_input_checking()

        if floatinputs == 0:
            return render_template("apology.html", message="Sorry, please check your inputs so that all values are greater than or equal to zero and are only numeric characters.")
        currentage = int(floatinputs[0])
        income = floatinputs[1]
        monthlycurrexpenses = floatinputs[2]
        stocks = floatinputs[3]
        bonds = floatinputs[4]
        cash = floatinputs[5]
        debt = floatinputs[6]
        monthlyretireexpenses = floatinputs[7]

        # get inputs that were numeric from form
        stockallocation = float(request.form.get("stockallocation"))
        stockinterest= float(request.form.get("stockreturn"))
        bondinterest = float(request.form.get("bondreturn"))

        # assume balance of investments that is not stocks is bonds
        bondallocation = 100 - stockallocation

        # collect calculator inputs to pass to render template of results.html
        inputs = {"Current Age":currentage,
                "Annual Income After Taxes":income,
                "Current Monthly Expenses":monthlycurrexpenses,
                "Monthly Retirement Expenses": monthlyretireexpenses,
                "Current Stock Holdings":stocks,
                "Current Bond Holdings":bonds,
                "Cash":cash,
                "Debt": debt,
                "Stock Allocation for Incoming Savings": stockallocation,
                "Bond Allocation for Incoming Savings": bondallocation,
                "Stock Annual Interest": stockinterest,
                "Bond Annual Interest": bondinterest
                }

        # Calcs
        annual_savings = income - 12 * monthlycurrexpenses
        if debt > 0:
            debt_payback_time = round(debt / annual_savings, 1) # payback time in years
        else:
            debt_payback_time = 0

        # calculate investment amount required for retirement
        retirement_nest_egg = monthlyretireexpenses * 12 / 0.04 #assume 4% safe withdrawal rate

        # calculate time to hit retirement investment amount
        annual_stock_contribution = (stockallocation/100)*annual_savings
        annual_bond_contribution = (bondallocation/100)*annual_savings

        # Generate net worth chart values without and with debt
        if debt_payback_time == 0:
            equation_inputs = (retirement_nest_egg, stocks, bonds, annual_stock_contribution, annual_bond_contribution, stockinterest, bondinterest)
            time_to_retirement = round(fsolve(equation, 20, args=equation_inputs)[0], 1)

            # info required to generate graphs
            extra_years = 4 # range beyond hitting retirement goal to chart
            time_labels = np.arange(start=0, stop=time_to_retirement + extra_years, step = 1)
            values = []

            for t in time_labels:
                value = invested_networth(t, stocks, bonds, annual_stock_contribution, annual_bond_contribution, stockinterest, bondinterest)
                values.append(round(value,2))

        else:
            # Assume initial stocks and bonds that are already invested will grow during debt payback period but annual stock/bond contribution is zero until debt is paid.
            stocks_appr = stocks * (1 + (stockinterest/100))**debt_payback_time
            bonds_appr = bonds * (1 + (bondinterest/100))**debt_payback_time
            equation_inputs = (retirement_nest_egg, stocks_appr, bonds_appr, annual_stock_contribution, annual_bond_contribution, stockinterest, bondinterest)
            time_to_retirement = round(fsolve(equation, 20, args=equation_inputs)[0] + debt_payback_time, 2)

            # info required to generate graphs
            extra_years = 4 # range beyond hitting retirement goal to chart
            time_labels = np.arange(start=0, stop=time_to_retirement + extra_years, step = 1)
            values = []

            for t in time_labels:
                if t <= debt_payback_time:
                    # if still paying back debt, set annual bond and stock contribution equal to 0
                    no_annual_stock_contribution = 0
                    no_annual_bond_contribution = 0
                    value = invested_networth(t, stocks, bonds, no_annual_stock_contribution, no_annual_bond_contribution, stockinterest, bondinterest)

                elif t == math.ceil(debt_payback_time):
                    # add in pro-rated annual stock and bond contributions after paying off debt to immediate year following debt payoff
                    fraction = math.ceil(debt_payback_time) - debt_payback_time
                    pro_rated_stock_contribution = fraction * annual_stock_contribution
                    pro_rated_bond_contribution = fraction * annual_bond_contribution
                    high_annual_stock_contribution = annual_stock_contribution + pro_rated_stock_contribution
                    high_annual_bond_contribution = annual_bond_contribution + pro_rated_bond_contribution
                    value = invested_networth(t, stocks, bonds, high_annual_stock_contribution, high_annual_bond_contribution, stockinterest, bondinterest)
                else:
                    # once out of debt contribute normal annual stock/bond contributions
                    value = invested_networth(t, stocks, bonds, annual_stock_contribution, annual_bond_contribution, stockinterest, bondinterest)
                values.append(round(value,2))

        # render the results HTML template
        return render_template("results.html", inputs=inputs, title="Projected invested assets ($) vs time (years)", max=retirement_nest_egg*1.5, labels=time_labels, values=values,
        retirement_nest_egg=retirement_nest_egg, time_to_retirement=time_to_retirement, debt_payback_time=debt_payback_time, monthlyretireexpenses=monthlyretireexpenses, annualsavings=annual_savings)
@app.route("/emily")

def emily():
    return render_template("emily.html")

@app.route("/About")
def About():
    return render_template("About.html")
