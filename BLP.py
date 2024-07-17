import blpapi
import pandas as pd

DATE = blpapi.Name("date")
ERROR_INFO = blpapi.Name("errorInfo")
EVENT_TIME = blpapi.Name("EVENT_TIME")
FIELD_DATA = blpapi.Name("fieldData")
FIELD_EXCEPTIONS = blpapi.Name("fieldExceptions")
FIELD_ID = blpapi.Name("fieldId")
SECURITY = blpapi.Name("security")
SECURITY_DATA = blpapi.Name("securityData")

# creation of the function which allow us to get data from Bloomberg
class BLP():
    
    def __init__(self): 
        """
            Improve this
            BLP object initialization
            Synchronus event handling
        """
        # Create Session object
        self.session = blpapi.Session()
        
        # Exit if can't start the Session
        if not self.session.start():
            print("Failed to start session.")
            return
        
        # Open & Get RefData Service or exit if impossible
        if not self.session.openService("//blp/refdata"):
            print("Failed to open //blp/refdata")
            return
        
        self.session.openService('//BLP/refdata')
        self.refDataSvc = self.session.getService('//BLP/refdata')

    
    def bdh(self, strSecurity, strFields, startdate, enddate, per='DAILY', perAdj = 'CALENDAR', days = 'NON_TRADING_WEEKDAYS', fill = 'PREVIOUS_VALUE', curr = "EUR"):
        
        # Create request
        request = self.refDataSvc.createRequest('HistoricalDataRequest')
        
        # Put field and securities in list is single value is passed
        if type(strFields) == str:
            strFields = [strFields]
            
        if type(strSecurity) == str:
            strSecurity = [strSecurity]
    
        # Append list of securities
        for strF in strFields:
            request.append('fields', strF)
    
        for strS in strSecurity:
            request.append('securities', strS)
    
        # Set other parameters
        request.set('startDate', startdate.strftime('%Y%m%d'))
        request.set('endDate', enddate.strftime('%Y%m%d'))
        request.set('periodicitySelection', per)
        request.set('nonTradingDayFillMethod',fill)
        request.set('nonTradingDayFillOption',days)
        request.set('currency',curr)
        request.set('periodicityAdjustment',perAdj)
        
        # Send request        
        requestID = self.session.sendRequest(request)
        
        # Receive request
        #-----------------------------------------------------------------------
        dict_Security_Fields={}
        list_msg=[]
        
        #creat as many empty dictionnaires as fields
        for field in strFields:
            globals()['dict_'+field]={}
        
        #traitement du résultat
        while True:
            event = self.session.nextEvent()
            # Ignores anything that's not partial or final
            if (event.eventType() !=blpapi.event.Event.RESPONSE) & (event.eventType() !=blpapi.event.Event.PARTIAL_RESPONSE):
                continue
            
            # Extract the response message
            for msg in blpapi.event.MessageIterator(event):
                list_msg.append(msg)
                
            # Break loop if response is final
            if event.eventType() == blpapi.event.Event.RESPONSE:
                break        
        
        #-----------------------------------------------------------------------
        # Exploit data 
        #-----------------------------------------------------------------------        
        for msg in list_msg:
            ticker = str(msg.getElement(SECURITY_DATA).getElement(SECURITY).getValue())

            for field in strFields:
                globals()['dict_' + field][ticker] = {}
                
            for field_data in msg.getElement(SECURITY_DATA).getElement(FIELD_DATA):
                dat=field_data.getElement(DATE).getValue()
                for i in range(1,(field_data.numElements())):
                    field_name = str(field_data.getElement(i).name())
                    try:
                        globals()['dict_'+field_name][ticker][dat]=field_data.getElement(i).getValueAsFloat()
                    except:
                        globals()['dict_'+field_name][ticker][dat]=field_data.getElement(i).getValueAsString()
                    
        for field in strFields:
            dict_Security_Fields[field]=pd.DataFrame.from_dict(globals()['dict_'+field],orient = 'columns')
            
        return dict_Security_Fields
    
    #-----------------------------------------------------------------------------------------------------

    def closeSession(self):
        print("Session closed")
        self.session.stop()