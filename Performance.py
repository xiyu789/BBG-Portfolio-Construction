import pandas as pd
import numpy as np
import datetime as dt


class Performance_Analysis():
    def __init__(self, df_ptf):
        self.df_ptf=df_ptf

    def daily_return(self):
        df_result = self.df_ptf.iloc[:,0].pct_change()
        df_result.dropna()
        return df_result
    
    def overall_performance(self):
        total_return = (self.df_ptf.iloc[-1,0] - self.df_ptf.iloc[0,0])/ self.df_ptf.iloc[0,0]
        return total_return

    def month_analysis(self):
        df=self.df_ptf
        df.index = pd.to_datetime(df.index)
        monthly_r = df.resample('M').apply(lambda x: (x.iloc[-1] / x.iloc[0] - 1) * 100)
        best_value = max(monthly_r.iloc[:,0])
        worse_value = min(monthly_r.iloc[:,0])
        best_month = df.isin([best_value]).any(axis=1).idxmax()
        worse_month = df.isin([worse_value]).any(axis=1).idxmax()
        result_df = pd.DataFrame({'time': [best_month, worse_month],'value': [best_value, worse_value]}, index=['best', 'worst'])
        return result_df
    
    def annualized_return(self):
        totalreturn = self.overall_performance()
        dayscount = (self.df_ptf.index[-1] - self.df_ptf.index[0]).days
        r_annualized = (1 + totalreturn) ** (365 / dayscount) -1
        return r_annualized


    def volatility(self, horizon):
        df_daily_r = self.daily_return()
        vol_daily = df_daily_r.std()
        if horizon == 'Daily':
            return vol_daily
        elif horizon == 'Monthly':
            return vol_daily*np.sqrt(21)
        else:
            return vol_daily*np.sqrt(252)

    def Sharpe_Ratio(self, rf):
        # here we ask the daily risk-free rate
        r_p = self.daily_return()
        rp = np.mean(r_p)
        sig_p = self.volatility('Daily')
        SH_P = np.sqrt(252) * (rp - rf)/sig_p
        SH_P = SH_P.iloc[0,0]
        return SH_P
  

    def Maximum_DD(self):
        day0 = self.df_ptf.index[0]
        MDD_bgn = dt.datetime(day0.year+1, day0.month, day0.day)
        df_MDD = pd.DataFrame(index=self.df_ptf.index)
        i=0
        for t in df_MDD.index:
            i+=1
            if t >= MDD_bgn:
                perf_range = self.df_ptf.iloc[:i+1,0]
                df_MDD.loc[t,0] = (min(perf_range) - max(perf_range))/max(perf_range)
        df_MDD.dropna()
        return df_MDD
    
    def hist_VaR(self, alpha):
        mtm_ptf = self.df_ptf.dropna().to_numpy()
        VaR = (np.percentile(mtm_ptf, alpha * 100)/self.df_ptf.iloc[0]-1) *100
        VaR = VaR.iloc[0]
        return VaR
