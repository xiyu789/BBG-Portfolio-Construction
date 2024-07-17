
import pandas as pd
from datetime import timedelta

import pandas_market_calendars as mcal

nyse = mcal.get_calendar('NYSE')

def z_score(tickers, date, blp):
    # initialize the dataframe
    df_zscore=pd.DataFrame(columns=['Stocks', 'Z-score'])
    # our horizon for the calculation of Z-score is 2 years
    bgn_horizon = date - timedelta(days=2*365)
    valid_bgn_horizon = mcal.date_range(nyse.schedule(start_date=bgn_horizon, end_date=date), frequency='1D')[0]
    # get historical prices of each stock
    hist_price = blp.bdh(tickers, ['PX_LAST'], valid_bgn_horizon, date)['PX_LAST']

    zscore = []
    for ticker in tickers:
        avg = hist_price[ticker].mean()
        std = hist_price[ticker].std()
        # z-score = (x - mean)/std
        z_score_value = (hist_price[ticker].iloc[-1] - avg) / std
        zscore.append({'Stocks': ticker, 'Z-score': z_score_value})
    
    df_zscore = pd.DataFrame(zscore)

    return df_zscore

