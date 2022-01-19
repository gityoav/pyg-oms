# -*- coding: utf-8 -*-

from pyg_base import dictattr

class Broker(dictattr):
    """
    Base class for Brokers. The broker class interacts with individual broker account
    holds information about the account such as:
    a) cash accounts, margin requirements
    b) costs of execution 
    c) margin account availability 

    """

    def __init__(self, account_id):
        self.account_id = account_id
        self.trades = self.get_working_trades() #initialization 
        self.positions = self.get_positions()
        self.cash = self.get_cash_accounts()
        
    def get_working_trades(self):
        return {}
    
    def get_positions(self):
        return {}
    
    def get_cash_accounts(self):
        return {}
    
    def send_trade(self, contract, order):
        pass
    
    def request_cancel(self, trade_id):
        pass
    
    def amend_trade(self, trade_id, amend):
        pass
    
    def cancel_trade(self, trade_id):
        pass
    
    def trade_status(self, trade_id):
        pass
    
    def fill_trade(self, trade_id, fill):
        pass

    def pre_trade_check(self, contract, order):
        return True

    def trade_cost(self, contract, order):
        return 0.0


        


