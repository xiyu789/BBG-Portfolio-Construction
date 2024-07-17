import pandas as pd
import datetime as dt

def get_data(lookback_horizon, country):
        """
        Loads Excel data from a specified sheet based on the country and lookback horizon.
        
        lookback_horizon (str): The lookback period to specify which Excel sheet to use.
        country (str): The country code to determine which Excel file to load.
        
        Returns: A DataFrame containing the data from the specified Excel sheet.
        """
        sheet_taken = str("Buyback_"+ lookback_horizon)
        
        if country == "US":
            df_database = pd.read_excel("ptf_RIY.xlsx",sheet_name = sheet_taken)
        elif country =="UK":
            df_database = pd.read_excel("ptf_UKX.xlsx",sheet_name = sheet_taken)
        else:
            df_database = pd.read_excel("ptf_SXXP.xlsx",sheet_name = sheet_taken)
        del df_database[df_database.columns[0]]
        return df_database


class Rebalance:
    def __init__(self, bgn_horizon, end_horizon, frequency):
        self.bgn_horizon = bgn_horizon
        self.end_horizon = end_horizon
        self.frequency = frequency

    def creat_lists(self, n):  
        lists=[]
        for i in range(50):
            lists.append(n*i)
        return lists

    def rebalance_freq(self): # list to get frequency months
        if self.frequency == "3M":
            month_list = self.creat_lists(3)
        elif self.frequency == "6M":
            month_list = self.creat_lists(6)
        else:
            month_list = self.creat_lists(12)
        return month_list

    def rebalance_month(self):
        """
        Generates a list of dates for rebalancing based on the specified frequency.
        
        The function extends the end horizon date by one year and generates dates at the end of each 
        rebalancing period starting from the beginning horizon date to one year after the end horizon date.
        
        Output:A list of dates representing the end of each rebalancing period.
        """
        end_horizon_date = dt.datetime.strptime(self.end_horizon, '%Y-%m-%d')
        end_horizon_date_next_year = end_horizon_date.replace(year=end_horizon_date.year + 1)
        end_date = end_horizon_date_next_year.strftime('%Y-%m-%d')
        if self.frequency == "3M":
            month_list = pd.date_range(start=self.bgn_horizon, end=end_date, freq='3ME')
        elif self.frequency == "6M":
            month_list = pd.date_range(start=self.bgn_horizon, end=end_date, freq='6ME')
        else:
            month_list = pd.date_range(start=self.bgn_horizon, end=end_date, freq='12ME')
        return month_list

    def next_rebalance(self, date):
        rebalance = self.rebalance_month()
        for i in range(len(rebalance)-1):
            if date > rebalance[i] and date <= rebalance[i+1]:
                return rebalance[i+1]