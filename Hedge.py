import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
import calendar

# from Data_Processing import Rebalance  # type: ignore


def get_point_value(country):
    # return int: The monetary value of a 1.0 point move in a futures contract for the specified country.
    if country == "US":
        return 5
    elif country == 'EU':
        return 50
    else:
        return 10
    

def futures_contract(actual_date, country, Rebalance):
    """
    Determines the appropriate futures contract ticker for each observation date,
    country-specific configurations, and specific year-month maturity rules.

    inputs:
        frequency (str): The rebalancing frequency.
        actual_date (datetime): The current date for which the contract is being determined.
        country (str): Country code to apply specific rules for futures contracts.

    output:
        str: The ticker symbol of the next applicable futures contract.
    """
    date = Rebalance.next_rebalance(date=actual_date)
    ticker_future = None
    if country == "US":
        ticket_letter = "HWA"
    elif country =="UK":
        ticket_letter =  "Z "
    else:  # Case EU
        ticket_letter = "SXO"
        
    # code for different maturity of futures contract
    month_codes = {'H': 3, 'M': 6, 'U': 9, 'Z': 12}
    for year in [date.year, date.year+1]:
        for code, month_futures in sorted(month_codes.items(), key=lambda x:x[1]):
            last_day = calendar.monthrange(year, month_futures)[1]
            contract_date = dt.datetime(year, month_futures, last_day)
            if date <= contract_date - timedelta(days=14):
                if ticker_future is None:
                    if year == 2023 and (code == 'H' or code =='M'):
                        ticker_future = ticket_letter + code + str(year)[-2:] + ' Index'
                    elif year < 2023:
                        ticker_future = ticket_letter + code + str(year)[-2:] + ' Index'
                    else:
                        ticker_future = ticket_letter + code + str(year)[-1] + ' Index'                                
    return ticker_future

def adjustment_futures_contract(dff, df_hedge, PX_futures):
    df_new_hedge = dff.loc[dff['Signal']=='Hedge'].reset_index(drop=True)
    df_new_sell = dff.loc[dff['Signal']=='Sell'].reset_index(drop=True)

    numerator = (df_new_hedge['Price'] * df_new_hedge['Quantity'] / df_new_hedge['Beta']).sum()
    # calculate the the number of futures contracts we should enter
    nb_futures = numerator/PX_futures
    qty_futures = np.floor(nb_futures).astype(int)

    if qty_futures == 0:
        # if the number of futures contracts entered is zero, then we sell all the products, regardless of the signal
        cash_sold = (dff['Price']*dff['Quantity']).sum()
    else:
        cash_sold = (df_new_sell['Price'] * df_new_sell['Quantity']).sum()
        # we also need to combine the new hedge dataframe to the previous one
        for i in range(df_new_hedge.shape[0]):
            stock_hedge = df_new_hedge.loc[i, 'Stocks']
            if stock_hedge in df_hedge['Stocks'].values:
                df_hedge.loc[df_hedge['Stocks']==stock_hedge, 'Quantity'] += df_new_hedge.loc[i, 'Quantity']
            else:
                df_new = df_new_hedge.iloc[[i]][['Stocks', 'Quantity']]
                df_hedge = pd.concat([df_hedge, df_new], ignore_index=True)
                
    result = [qty_futures, cash_sold, df_hedge]
    return result
