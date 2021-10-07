# F.I.R.E. Calculator Web Application

#### Web application URL:

https://fire-web-app.herokuapp.com/

#### Video Demo:

https://youtu.be/Tm-WQscB2-s

#### Description:

The F.I.R.E (financial independence retire early) calculator web application is a tool to estimate when the user can reach "financial independence" and retire early.
The inspiration of this project was to help people become more financially aware of how much money they need to fund their lifestyle during retirement, and how small changes can add up quickly with compound interest.
The navbar includes links to 3 pages: FIRE calculator (index.html), About Fire (about.html), and About Emily (emily.html).

The index (homepage) consists of a form where the user will input their financial information such as monthly expenses, annual after-tax income, etc and then hit submit to project their retirement age and net worth required to retire. If the user puts in values that includes symbols other than "$", ".", or "," the application redirects to an apology page asking the user to check their input.

After hitting submit, the user will be directed to the results.html page (not listed in the navbar) This page displays the values of the inputs from the home page in a table, text telling the user the nest egg required to retire

There is also a Chart.js graph showing the user's net worth in investments over time. The data generated for the chart used numpy to create arrays for the x-axis.

The user can also learn more about the concept of FIRE by clicking on the "About Fire" page on the navbar(about.html). This page describes the basis of the 4% rule, while says that your total investments in retirement multiplied by 4% should be equal to your annual retirement spend.

This page explains the concepts of FIRE and offers some advice on how to invest and budget to achieve financial independence such as investing consistently in total stock market index funds.

The "About Emily" page on the navbar directs to a page with a short bio about the creator with a link via the Linkedin icon to her LinkedIn page and a picture.

The layout.html page provides the layout for each html page using Jinja to extend the layout and add content with blocks/placeholders.

The styles.css page includes the CSS styles utilized on each of the HTML pages.

The backend of the web app is in the file application.py. The calculations that are displayed on the results page are all done in this file. The nest egg required to retire is calculated by taking the annual expenditure in retirement and dividing by 0.04 (the 4% rule).
The time required to achieve the nest egg is calculated numerically with python's fsolve using the inputted annual interest rates for stocks and bonds inputted by the user.

The web application utilizes python, flask, javascript, HTML, and CSS.

#### Requirements
Python
Flask
Requests
Scipy fsolve
math



