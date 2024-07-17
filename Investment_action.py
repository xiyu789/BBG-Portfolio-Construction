
import pandas as pd

def beginning(df_price, capital_invest):
    """
    Initializes investment information based on current prices and capital investment.
    
    df_price (DataFrame): Current prices of stocks. Columns are stock symbols, and rows are time series data.
    capital_invest (float): The total capital to be invested.
    
    output: A DataFrame containing the initial investment details including price and quantity per stock
    """
    df_info = pd.DataFrame()
    df_info['Stocks'] = df_price.columns
    df_info['Price'] = df_price.iloc[0,:].reset_index(drop=True)
    df_info['Money_invested'] = capital_invest / len(df_price.columns)
    df_info['Theoretical_Quantity'] = df_info['Money_invested']/df_info['Price']
    # Adjustment of the quantity to integer, then recalculate the money_invested & the cash remained
    df_info['Quantity'] = df_info['Theoretical_Quantity'].apply(int)
    df_info['Actual_Money_Inv'] = df_info['Quantity'] * df_info['Price']
    return df_info

def ending(df_info, df_price, df_zscore, df_beta):
    """
    Generates signals for each stock based on the ending prices, z-scores, and betas.
    
    df_info (DataFrame): Initial investment information including quantities and stocks.
    df_price (DataFrame): Current prices of stocks at the end of the period.
    df_zscore (DataFrame): Z-scores for the stocks to generate buy/sell signals.
    df_beta (DataFrame): Current beta values for the stocks.
    
    output: A DataFrame containing the ending prices, quantities, z-scores, signals (sell or hedge), and beta values for each stock.
    """
    threshold = -1
    df_signal = pd.DataFrame()
    df_signal['Stocks'] = df_price.columns
    
    # check if the dimension of each dataframe are not identical
    if df_price.columns.tolist() != df_info['Stocks'].tolist():
        print("\nPRICE AND INFO MISMATCH")
    if df_info['Stocks'].tolist() != df_zscore['Stocks'].tolist():
        print("INFO AND Z_SCORE MISMATCH \n")

    df_signal['Price'] = df_price.iloc[-1,:].reset_index(drop=True)
    df_signal['Quantity'] = df_info['Quantity']
    df_signal['Z-score'] = df_zscore.iloc[:,1]
    df_signal['Signal'] = ["Sell" if df_zscore.iloc[col, 1] > threshold else "Hedge" for col in range(df_zscore.shape[0])]
    df_signal['Beta'] = df_beta.iloc[-1,:].reset_index(drop=True)
    return df_signal

def calculate_ptf_value(df_ptf, df_price, cash_value):
    df_value = pd.DataFrame(index=df_price.index)
    if df_ptf.shape[0] != df_price.shape[1]:
        # wich means the number of stocks for the dataframe saved quantity is not equivalent to that of price
        # dimension mismatch
        print(df_ptf.shape[0])
        print(df_price.shape[1])
        print("\nDimension Price not corresponds to the Dimension Quantity!\n")
    else:
        for i in df_price.index:
            sum_val=0
            for j in df_ptf.index:
                stock_name = df_ptf.loc[j, 'Stocks']
                sum_val += df_ptf.loc[j, 'Quantity'] * df_price.loc[i, stock_name]
            df_value.loc[i, 'ptf_value'] = sum_val + cash_value
    return df_value


def regenerate_orders(df_info_stay, df_new_info, df_price):
    """  
    inputs:
    df_info_stay: DataFrame containing existing stock information.
    df_new_info: DataFrame containing new stock information.
    df_price: DataFrame whose columns represent stock orders to be matched.
    
    ouput: df_info (pd.DataFrame): A reordered DataFrame with rows matching the columns of df_price.
    """
    # reform the database of df_info_stay
    for i in range(df_info_stay.shape[0]):
        df_info_stay.loc[i, 'Price'] = df_price.loc[df_price.index[0], df_info_stay.loc[i, 'Stocks']]
        df_info_stay.loc[i, 'Money_invested'] = df_info_stay.loc[i, 'Price'] * df_info_stay.loc[i, 'Theoretical_Quantity']
        df_info_stay.loc[i, 'Actual_Money_Inv'] = df_info_stay.loc[i, 'Price'] * df_info_stay.loc[i, 'Quantity']
 
    df_ptf=pd.concat([df_info_stay, df_new_info], ignore_index = True)
    df_info = pd.DataFrame(columns=df_ptf.columns, index=df_ptf.index)

    for i in range(len(df_price.columns)):
        stock_order = df_price.columns[i]
        if stock_order in df_ptf['Stocks'].values:
            row_index = df_ptf.index[df_ptf['Stocks'] == stock_order][0]
            df_info.iloc[i,:]= df_ptf.iloc[row_index,:]
        else:
            print("stock", df_price.columns[i], " not found in df_ptf !!!")
    return df_info


def identify_action(tickers, df_info, df_signal):
    """
    This function identifies the stocks to be bought and excluded for the next month's portfolio.
    
    inputs:
    tickers (list): List of new portfolio components for the next month.
    df_info: DataFrame containing the current portfolio information.
    df_signal: DataFrame containing signals for the stocks.
    
    outputs:
    list: Stocks to be bought.
    df_info_stay (pd.DataFrame): Updated DataFrame with remaining stocks for the next month.
    dff (pd.DataFrame): DataFrame with signals for stocks to be excluded.
    """
    # get the previous & the following month's portfolio components
    prev_components = df_info.loc[:,'Stocks']
    new_components = tickers
    # identify which should be disappeared for the new month, and the ones should be added
    to_exclude = prev_components[~prev_components.isin(new_components)].reset_index(drop=True)
    to_buy = new_components[~new_components.isin(prev_components)].tolist()
    df_info_stay = df_info.loc[~df_info.loc[:,'Stocks'].isin(to_exclude), :].reset_index(drop=True)

    # identify the signal of each stock need to be excluded for the next-month's portfolio
    dff = df_signal[df_signal.loc[:,'Stocks'].isin(to_exclude)]
    dff = dff.reset_index(drop=True)

    return to_buy, df_info_stay, dff


def buying_new_components(to_buy, cash_sold, cash, new_cash_use_percent, df_price_cur):
    if len(to_buy)>0:
        cash_use = cash_sold + cash * new_cash_use_percent
        df_info = beginning(df_price_cur[to_buy], cash_use)
        cash = cash + cash_sold - df_info['Actual_Money_Inv'].sum()
    else:    
        df_info = pd.DataFrame(columns=['Stocks', 'Price', 'Money_invested', 'Theoretical_Quantity', 'Quantity', 'Actual_Money_Inv'])

    return df_info, cash


def reevaluatation_ptf(df_futures, df_value, valid_bgn_date, pt_value, blp):
    print(df_futures)
    ticker_futures = df_futures.loc[0, 'Ticker']
    PX_index = blp.bdh(strSecurity=ticker_futures, strFields=['PX_LAST'], startdate=valid_bgn_date.date(), enddate=valid_bgn_date.date())
    payoff_futures = (df_futures['Price'] * df_futures['Quantity']).sum() - PX_index['PX_LAST'].iloc[0, 0] * pt_value * (df_futures['Quantity'].sum())
    value_ptf = df_value.iloc[-1, 0] + payoff_futures
    return value_ptf, payoff_futures