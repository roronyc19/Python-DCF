#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 12:56:09 2021

**RUN THIS FILE FIRST**

Change "company" variable to the ticker (e.g. AAPL) of whatever 
company you would like to perform a Discounted Cash Flow on 

Assumptions are to be entered in '{ticker} financials formatted.xlsx'
in the years that begin with "Growth"

Most default to the 3 year averages but these assumptions may not
reflect true expectations, which must be inputted manually in the
excel file

@author: roronyc19
"""

#import requests
import pandas as pd
import numpy as np
import os
import urllib.request 

# Change this
company = 'AAPL'

# My API Key -- if this runs out replace with new key by creating
# free account at financialmodelingprep.com
demo = 'd261c89ac2bbf96c836dbf9fa755ab1a'


#years = '12'
# IS = requests.get(f'https://financialmodelingprep.com/api/v3/income-statement/{company}?limit={years}&apikey={demo}').json()

# #%%
# import csv
# #import urllib3
# from urllib.request import urlopen
# response = urlopen(f'https://financialmodelingprep.com/api/v3/income-statement/{company}?datatype=csv&apikey={demo}')
# cr = csv.reader(response)
#%% ignore above


#import 10y historical balance sheets, income statement, cash flows

newpath = os.path.join(os.getcwd(), f'{company}docs')

if not os.path.exists(newpath):
    os.makedirs(newpath)

urllib.request.urlretrieve(f'https://financialmodelingprep.com/api/v3/income-statement/{company}?datatype=csv&apikey={demo}', os.path.join(newpath,f'{company} IS.csv'))
urllib.request.urlretrieve(f'https://financialmodelingprep.com/api/v3/cash-flow-statement/{company}?datatype=csv&apikey={demo}', os.path.join(newpath,f'{company} CF.csv'))
urllib.request.urlretrieve(f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{company}?datatype=csv&apikey={demo}', os.path.join(newpath,f'{company} BS.csv'))

                           
#%%


dates = pd.read_csv(os.path.join(newpath,f'{company} BS.csv'), nrows=1)
#dates.rename(columns={"Unnamed: 1":""})
cfs = pd.read_csv(os.path.join(newpath,f'{company} CF.csv'), skiprows=1,header=None,usecols = [i for i in range(1,len(dates.columns))], names = dates.columns[1:])
bss = pd.read_csv(os.path.join(newpath,f'{company} BS.csv'),skiprows=1,header=None,usecols = [i for i in range(1,len(dates.columns))], names = dates.columns[1:])
iss = pd.read_csv(os.path.join(newpath,f'{company} IS.csv'), skiprows=1,header=None,usecols = [i for i in range(1,len(dates.columns))], names = dates.columns[1:])

pd.set_option('use_inf_as_na', True) #keep?

cfsrowlabs = cfs.loc[:,dates.columns[1:3]].dropna()
cfsrowlabs = cfsrowlabs.loc[:,dates.columns[1:2]]
cfs = cfs.loc[:,dates.columns[2:]].dropna(how='all')
cfs.index = cfsrowlabs # add rows labels
cfs.index = cfs.index.map("".join) #remove faulty format
cfs.rename(columns=lambda s: s[:4],inplace=True) #cut to year
cfs = cfs.T # makes years rows


bssrowlabs = bss.loc[:,dates.columns[1:3]].dropna()
bssrowlabs = bssrowlabs.loc[:,dates.columns[1:2]]
bss = bss.loc[:,dates.columns[2:]].dropna(how='all')
bss.index = bssrowlabs # add rows labels
bss.index = bss.index.map("".join) #remove faulty format
bss.rename(columns=lambda s: s[:4],inplace=True) #cut to year
bss = bss.T # makes years rows

issrowlabs = iss.loc[:,dates.columns[1:3]].dropna()
issrowlabs = issrowlabs.loc[:,dates.columns[1:2]]
iss = iss.loc[:,dates.columns[2:]].dropna(how='all')
iss.index = issrowlabs # add rows labels
iss.index = iss.index.map("".join) #remove faulty format
iss.rename(columns=lambda s: s[:4],inplace=True) #cut to year
iss = iss.T # makes years rows

#%% projection time
arr = iss["revenue"].to_numpy()
arryoy = arr[:-1]/arr[1:]
arr3y = [sum(arryoy[i:i+3])/3 for i in range(len(arryoy-3))]
iss.insert(0,"revGrowth", np.append(arryoy,[None]*(len(iss.index)-len(arryoy)) ) )

#%%

iss.insert(0, "RnD/rev", iss.ResearchAndDevelopmentExpenses / iss.revenue)
iss.insert(0, "SGA/rev", (iss.GeneralAndAdministrativeExpenses + iss.SellingAndMarketingExpenses) / iss.revenue)
iss.insert(0, "other/rev", (iss.otherExpenses) / iss.revenue)

iss.insert(0, "int/ltd", iss.interestExpense / bss.longTermDebt)
iss["int/ltd"] = iss["int/ltd"].fillna(0)

iss.insert(0, "taxRate", iss.incomeTaxExpense / iss.incomeBeforeTax )
iss.insert(0, "DnA/rev", iss.depreciationAndAmortization / iss.revenue)
iss.insert(0, "capex/rev", -1* cfs.capitalExpenditure / iss.revenue)
iss.insert(0, "NWC", bss.totalCurrentAssets - bss.cashAndShortTermInvestments - bss.totalCurrentLiabilities)
iss.insert(0, "NWC/rev", iss.NWC/ iss.revenue)
#%%
arr = iss["NWC"].to_numpy()
deltanwc = arr[:-1]-arr[1:]
iss.insert(0,"deltaNWC", np.append(deltanwc,[None]*(len(iss.index)-len(deltanwc)) ) )
iss.insert(0,"deltaNWC/rev", iss.deltaNWC/iss.revenue )
#%%

iss.insert(0, "ImpliedEBIT", iss.grossProfitRatio-iss["SGA/rev"]- iss["RnD/rev"] )
iss.insert(0, "ImpliedEBT", iss.ImpliedEBIT *(1- iss["int/ltd"] ))
#actual EBT incomeBeforeTax
iss.insert(0, "OperErn/rev(calc)", iss.ImpliedEBT *(1- iss["taxRate"] ))
iss.insert(0, "OperErn/rev(given)", iss.operatingIncomeRatio)
iss.insert(0, "ImpliedFCF/rev(calc)", iss["OperErn/rev(calc)"]-iss["capex/rev"]+iss["DnA/rev"]-iss["deltaNWC/rev"])
iss.insert(0, "ImpliedFCF/rev(given)", iss["OperErn/rev(given)"]-iss["capex/rev"]+iss["DnA/rev"]-iss["deltaNWC/rev"])
# - change NWC
#%%
iss = iss.fillna(0) #??

yrs = [3,5,10]
isratios = ["revGrowth","grossProfitRatio",'SGA/rev', 'RnD/rev','other/rev','int/ltd',\
            'taxRate','DnA/rev','capex/rev','NWC/rev','ImpliedEBIT','ImpliedEBT',\
            'OperErn/rev(given)', 'OperErn/rev(calc)','ImpliedFCF/rev(calc)',\
            'ImpliedFCF/rev(given)']

gprs = [ [ sum(iss[r].iloc[0:y])/y for y in yrs if y <= len(iss.index)] for r in isratios]
cols = ["3yAvg","5yAvg","10yAvg"]

avgs = pd.DataFrame(gprs,index =isratios,columns=cols[:len(gprs[0])])
avgs = avgs.T

proj = avgs.append(avgs.loc["3yAvg"][:-6], [None]*6)
proj = proj.append(avgs.loc["3yAvg"][:-6], [None]*6)
proj = proj.append(avgs.loc["3yAvg"][:-6], [None]*6)

l = [1.04]+ [None]*(len(avgs.columns)-1)
proj.loc[len(proj)] = l

l2 = [1.09]+ [None]*(len(avgs.columns)-1)
proj.loc[len(proj)] = l2

cols.extend(["Growth Yrs 1-2","Growth Yrs 3-5",\
                          "Growth Yrs 6-10", "Terminal Growth", \
                              "Discount Rate"])
    
proj.index = cols
proj.loc["Growth Yrs 3-5"][0] = 1 + (proj.loc["Growth Yrs 3-5"][0]-1)/1.5
proj.loc["Growth Yrs 6-10"][0] = 1 + (proj.loc["Growth Yrs 3-5"][0]-1)/2.5


avgs = proj
#avgs = avgs.rename_axis(f"{company}", axis=1)
# for n in ["Growth Yrs 1-2","Growth Yrs 3-5","Growth Yrs 6-10", "Terminal Growth"]:
#     avgs = avgs.append(pd.Series(name=n))

#avgs.append("Growth")
#%%
# byreviss = ["ResearchAndDevelopmentExpenses", "GeneralAndAdministrativeExpenses","SellingAndMarketingExpenses","otherExpenses"]
# for r in byreviss:
    
#     arr = iss["revenue"].to_numpy();
#     arryoy = arr[:-1]/arr[1:]

# hist = [ [ sum(iss[r].iloc[0:y])/(y*[ sum(iss["revenue"].iloc[0:y]) ) for y in yrs] for r in isratios] ]
# iss.insert(0, "2020 %rev ", iss["2020"]/iss["2020"].iloc[0])

#%%

#pd.options.display.float_format = '{:.2%}'.format

# cfs.to_csv(f'{company} cf formatted.csv')
# bss.to_csv(f'{company} bs formatted.csv')
# iss.to_csv(f'{company} is formatted.csv')
avgs = avgs*100
avgs['revGrowth'] -= 100


iss[iss>1000] /= 1000000
iss[iss<-1000] /= 1000000

bss[bss>1000] /= 1000000
bss[bss<-1000] /= 1000000

cfs[cfs>1000] /= 1000000
cfs[cfs<-1000] /= 1000000

avgs = avgs.round(1)
iss = iss.round(3)
cfs = cfs.round(3)
bss = bss.round(3)

fpath =f'{company} financials formatted.xlsx'
writer = pd.ExcelWriter(fpath, engine='xlsxwriter')
avgs.to_excel(writer,sheet_name="Average Financials")
iss.to_excel(writer,sheet_name="Income Statement & Financials")
cfs.to_excel(writer, sheet_name="Cash Flow Statement")
bss.to_excel(writer, sheet_name="Balance Sheet")

writer.save()

