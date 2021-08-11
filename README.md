# Python-DCF
## Performs a Discounted Cash Flow analysis of any publicly traded company 

## * Uses the FinancialModelingPrep API to pull financial data using any companies ticker symbol (e.g. AAPL for Apple Inc.) 
## * Using this data, the program formats and outputs an excel file that the user can edit to build in revenue growth, gross margin, opex, etc. assumptions that are by default set to their 3y average

## * Once growth assumptions are inputted, a DCF analysis is performed and the program outputs the calcultions and a final fair value price to an excel file

# How to run

## 1.) Naviagate to "statementscraper.py" file

### * Ensure all imported packages are downloaded and available
### * Change "company" variable to the ticker (e.g. AAPL) of whatever 
###   company you would like to perform a Discounted Cash Flow on 
### * Run the file in whatever editor you like
### * Assumptions are to be entered in '{ticker} financials formatted.xlsx'
###   in the years that begin with "Growth"
### * Most default to the 3 year averages but these assumptions may not
###   reflect true expectations, which must be inputted manually in the excel file

## 2.) Change any assumptions in the Average Financials Tab in the '{ticker} financials formatted.xlsx'

## 3.) Once satisfied with assumptions, navigate to "cashflowmaker.py"

### * Once again, ensure the "company" variable matches the company ticker you want the DCF for 
