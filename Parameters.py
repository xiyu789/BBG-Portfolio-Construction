import tkinter as tk
from tkinter import messagebox

class Portfolio_GUI:
    def __init__(self, root):
        self.root = root
        root.title("Portfolio Input Parameters")
        
        # Labels and input value for country, start date, capital, lookback horizon, liquid reserves, and frequency
        tk.Label(root, text="Country (US/UK/EU):").grid(row=0, column=0)
        self.country_input = tk.Entry(root)
        self.country_input.grid(row=0, column=1)
        self.country_input.insert(0, "US")

        tk.Label(root, text="Capital :").grid(row=2, column=0)
        self.capital_input = tk.Entry(root)
        self.capital_input.grid(row=2, column=1)
        self.capital_input.insert(0,"10000000")

        tk.Label(root, text="Liquid Reserve (%):").grid(row=3, column=0)
        self.liquid_reserves_input = tk.Entry(root)
        self.liquid_reserves_input.grid(row=3, column=1)
        self.liquid_reserves_input.insert(0, "45.0") 

        tk.Label(root, text="Lookback Horizon (1y/2y/3y):").grid(row=4, column=0)
        self.lookback_horizon_input = tk.Entry(root)
        self.lookback_horizon_input.grid(row=4, column=1)
        self.lookback_horizon_input.insert(0, "1y") 

        tk.Label(root, text="Frequency (3M/6M/12M):").grid(row=5, column=0)
        self.frequency_input = tk.Entry(root)
        self.frequency_input.grid(row=5, column=1)
        self.frequency_input.insert(0,"3M")
        

        # Submit button
        tk.Button(root, text="Submit", command=self.submit_info).grid(row=6, columnspan=2)

        # Initialize attributes to store the input values
        self.country = None
        #self.start_date = None
        self.capital = None
        self.liquid_reserves = None
        self.frequency = None
        self.lookback_horizon = None

        # Label for displaying messages
        self.message = tk.Label(root, text="", fg="red")
        self.message.grid(row=7, columnspan=2)

    def submit_info(self):
        # Collecting the information
        self.country = self.country_input.get()
        self.capital = float(self.capital_input.get())
        self.liquid_reserves = float(self.liquid_reserves_input.get()) / 100
        self.lookback_horizon = self.lookback_horizon_input.get()
        self.frequency = self.frequency_input.get()

        # Example processing: Show the information in a message box or do further processing
        info = f"Country: {self.country} \nCapital: {self.capital}\n" \
           f"Liquid Reserves: {self.liquid_reserves}\n" \
           f"Lookback Horizon: {self.lookback_horizon}\nFrequency: {self.frequency}"
        messagebox.showinfo("Submitted Information", info)

        #close interface
        self.root.destroy()


class Rf_index:
    def __init__(self, country):
        self.__country = country
    
    def rf_Index(self):
        if self.__country == 'US':
            rf = 'USGG10YR Index'
        elif self.__country == 'UK':
            rf = 'GUKG10 Index'
        else:
            rf = 'GDBR10 Index'
        return rf
