"""
Created on Tues Jul 13 12:57:29 2021

**IMPORTANT**
1) Run this file AFTER statementscraper.py
2) Ensure the company variable matches that in statementscraper.py

This code will output an excel file named '{ticker} Cash Flow.xlsx'
containing the dcf calculations and final output

@author: roronyc19
"""

#import requests
import pandas as pd

# ensure this 
company = 'AAPL'

fins = pd.read_excel(f"{company} financials formatted.xlsx" ,index_col = 0, sheet_name=0)
inc = pd.read_excel(f"{company} financials formatted.xlsx",index_col = 0, sheet_name=1)
bss = pd.read_excel(f"{company} financials formatted.xlsx",index_col = 0, sheet_name=3)
cfs = pd.read_excel(f"{company} financials formatted.xlsx",index_col = 0, sheet_name=2)


cols = [i for i in range(0,10)]


rows = ['revenue', 'growthRate', 'grossMargin', 'grossProfit', 'SGA/rev', 'SGA', \
        'RnD/rev', 'RnD', 'other/rev', 'other', 'operatingMargin', 'operatingProfit', \
        'int/ltd', 'ltd','intExp', 'EBT', 'taxRate', 'earningsMargin', \
        'earnings', 'EPS', 'DnA/rev', 'DnA', 'capex/rev', 'capex', 'NWC/rev', 'NWC', \
        'deltaNWC', 'FCF/rev', 'FCF', 'FCFgrowthRate', 'discountRate', 'discountedFCF']


#year 0
list = [inc.revenue.iloc[0], \
        None, \
        inc["grossProfitRatio"].iloc[0], \
        inc["grossProfitRatio"].iloc[0] * inc.revenue.iloc[0], \
        inc["SGA/rev"].iloc[0], \
        inc["SGA/rev"].iloc[0] * inc.revenue.iloc[0], \
        inc["RnD/rev"].iloc[0], \
        inc["RnD/rev"].iloc[0] * inc.revenue.iloc[0], \
        inc["other/rev"].iloc[0], \
        inc["other/rev"].iloc[0] * inc.revenue.iloc[0], \
        inc["operatingIncomeRatio"].iloc[0], \
        inc["operatingIncomeRatio"].iloc[0] * inc.revenue.iloc[0], \
        inc["int/ltd"].iloc[0], \
        bss["longTermDebt"].iloc[0], \
        inc["int/ltd"].iloc[0] * bss["longTermDebt"].iloc[0], \
        inc["ImpliedEBT"].iloc[0] * inc.revenue.iloc[0], \
        inc["taxRate"].iloc[0], \
        inc["OperErn/rev(calc)"].iloc[0], \
        inc["OperErn/rev(calc)"].iloc[0] * inc.revenue.iloc[0], \
        inc["OperErn/rev(calc)"].iloc[0] * inc.revenue.iloc[0] \
            / inc["weightedAverageShsOutDil"].iloc[0], \
        inc["DnA/rev"].iloc[0], \
        inc["DnA/rev"].iloc[0] * inc.revenue.iloc[0], \
        inc["capex/rev"].iloc[0], \
        inc["capex/rev"].iloc[0] * inc.revenue.iloc[0], \
        inc["NWC/rev"].iloc[0], \
        inc["NWC"].iloc[0], \
        inc["deltaNWC"].iloc[0], \
        inc["ImpliedFCF/rev(calc)"].iloc[0], \
        inc["ImpliedFCF/rev(calc)"].iloc[0] * inc.revenue.iloc[0], \
        None, \
        1.00, \
        inc["ImpliedFCF/rev(calc)"].iloc[0] * inc.revenue.iloc[0]  ]
 

df = pd.DataFrame(list, index=rows, columns=['0'])


#%%
rates = ['Growth Yrs 1-2','Growth Yrs 3-5', 'Growth Yrs 6-10']

#years 1-2
y = 1
for y in range(1,11):
    if y<3:
        rate = rates[0]
    elif y<6:
        rate = rates[1]
    else:
        rate = rates[2]
    
    df[f'{y}'] = df[f'{y-1}'] #cp prev yrs
    df.at['revenue', f'{y}'] *= (1+(fins.at[f'{rate}','revGrowth']/100) )
    df.at['growthRate', f'{y}'] = (1+(fins.at[f'{rate}','revGrowth']/100) )
    
    rev = df.at['revenue', f'{y}']    
    grossMargin = fins.at[f'{rate}','grossProfitRatio']/100
    sga = fins.at[f'{rate}','SGA/rev']/100
    rnd = fins.at[f'{rate}','RnD/rev']/100
    other = fins.at[f'{rate}','other/rev']/100
    operMarg = grossMargin - sga - rnd - other
    operInc = operMarg*rev
    
    intltd = fins.at[f'{rate}','int/ltd']/100
    ltd = df.at['ltd',f'{y-1}']
    intr = intltd*ltd
    ebt = operInc - intr
    
    taxrate = fins.at[f'{rate}','taxRate']/100
    earnings = (1-taxrate)*ebt
    earnmarg = earnings/rev
    shares = inc["weightedAverageShsOutDil"].iloc[0]
    eps = earnings/shares
    
    dna = fins.at[f'{rate}', 'DnA/rev']/100
    capex = fins.at[f'{rate}', 'capex/rev']/100
    nwc = fins.at[f'{rate}', 'NWC/rev']/100
    delnwc = nwc*rev - df.at['NWC', f'{y-1}']
    fcf = earnings-capex+dna-delnwc
    fcfbyrev = fcf/rev
    fcfgrowth = 100*(fcf / df.at['FCF', f'{y-1}'] - 1)
    discount = df.at['discountRate', f'{y-1}'] * (1+(fins.at['Discount Rate','revGrowth']/100))
    fcfPV = fcf/discount 
    
    
    df.at['grossMargin', f'{y}'] = grossMargin
    df.at['grossProfit', f'{y}'] = grossMargin*rev
    
    df.at['SGA/rev', f'{y}'] = sga
    df.at['SGA', f'{y}'] = sga *rev
    df.at['RnD/rev', f'{y}'] = rnd
    df.at['RnD', f'{y}'] = rnd *rev
    df.at['other/rev', f'{y}'] = other
    df.at['other', f'{y}'] = other*rev
    
    df.at['operatingMargin', f'{y}'] = operMarg
    df.at['operatingProfit', f'{y}'] = operMarg * rev
    
    df.at['int/ltd', f'{y}'] = intltd
    df.at['ltd', f'{y}'] = ltd
    df.at['intExp', f'{y}'] = intr
    df.at['EBT', f'{y}'] = ebt
    
    df.at['taxRate', f'{y}'] = taxrate
    df.at['earningsMargin', f'{y}'] = earnmarg
    df.at['earnings', f'{y}'] = earnings
    df.at['EPS', f'{y}'] = eps
    
    df.at['DnA/rev', f'{y}'] = dna
    df.at['DnA', f'{y}'] = dna*rev
    df.at['capex/rev', f'{y}'] = capex
    df.at['capex', f'{y}'] = capex*rev
    df.at['NWC/rev', f'{y}'] = nwc
    df.at['NWC', f'{y}'] = nwc*rev
    df.at['deltaNWC',f'{y}'] = delnwc
    
    df.at['FCF/rev', f'{y}'] = fcfbyrev
    df.at['FCF', f'{y}'] = fcf
    df.at['FCFgrowthRate', f'{y}'] = fcfgrowth
    df.at['discountRate', f'{y}'] = discount
    df.at['discountedFCF', f'{y}'] = fcfPV
    
#%%
res = fins   

res = res.append(pd.Series(name='Sum PVs 1-10'))
fcfsum = sum(df.loc["discountedFCF",'1':])
res.at['Sum PVs 1-10','revGrowth'] = fcfsum

res = res.append(pd.Series(name='Yr 10 FCF'))
res.at['Yr 10 FCF','revGrowth'] = df.loc["FCF",'10']

res = res.append(pd.Series(name='PV Yr 10 FCF'))
res.at['PV Yr 10 FCF','revGrowth'] = df.loc["discountedFCF",'10']

termgrowth = res.at['Terminal Growth', 'revGrowth']/100
discount = res.at['Discount Rate', 'revGrowth']/100

res = res.append(pd.Series(name='Terminal Value Y10*(1+g)/(r-g)'))
termval = df.loc["discountedFCF",'10'] *(1+ termgrowth) / (discount-termgrowth)
res.at['Terminal Value Y10*(1+g)/(r-g)','revGrowth'] = termval


res = res.append(pd.Series(name='Implied EV/FCF Multiple'))
res.at['Implied EV/FCF Multiple','revGrowth'] = 1/(discount-termgrowth)

res = res.append(pd.Series(name=f'{company} EV'))
res.at[f'{company} EV','revGrowth'] = fcfsum+termval

res = res.append(pd.Series(name='Net Debt (LTD-Cash)'))
cash = bss["totalCurrentAssets"].iloc[0]
longdebt = bss["longTermDebt"].iloc[0]
res.at['Net Debt (LTD-Cash)','revGrowth'] = longdebt-cash

res = res.append(pd.Series(name='Equity Value (EV-netDebt)'))
res.at['Equity Value (EV-netDebt)','revGrowth'] = fcfsum+termval-longdebt+cash

res = res.append(pd.Series(name='Shares Outstanding'))
res.at['Shares Outstanding','revGrowth'] = shares

res = res.append(pd.Series(name='Intrinsic Value (Local Curr)'))
res.at['Intrinsic Value (Local Curr)','revGrowth'] = res.at['Equity Value (EV-netDebt)','revGrowth'] /shares

res = res.append(pd.Series(name='Good Entry (75% Intrinsic)'))
res.at['Good Entry (75% Intrinsic)', 'revGrowth'] = res.at['Intrinsic Value (Local Curr)','revGrowth']  * 0.75

res = res.round(2)
df = df.round(2)

writer = pd.ExcelWriter(f'{company} Cash Flow.xlsx', engine='xlsxwriter')
res.to_excel(writer,sheet_name="Cash Flow Result")
df.to_excel(writer,sheet_name="Cash Flow Comp")
writer.save()
#json = urllib.request.urlretrieve(f'https://financialmodelingprep.com/api/v3/quote/{company}')









