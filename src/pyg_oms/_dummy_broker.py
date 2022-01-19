from pyg_oms._broker import Broker
from pyg_oms._order import Fill, Order
from pyg_base import dictable
import numpy as np

class DummyBroker(Broker):
    """         
        self.account_id = account_id
        self.trades = self.get_working_trades() #initialization 
        self.positions = self.get_positions()
        self.cash = self.get_cash_accounts()
    """
    def __init__(self, account_id):
        super(DummyBroker, self).__init__(account_id)
        self._trade_id = 0

    def get_working_trades(self):
        return {}
    
    def get_positions(self):
        return {}
        
    def send_trade(self, contract, order):
        self._trade_id += 1
        tid = self._trade_id        
        order.open = order.qty
        order.trade_id = tid 
        order.status = 'open'
        order.filled = 0
        order.price = np.nan
        self.trades[tid] = (contract, order)
        self.fills[tid] = dictable()
        return tid
    
    def request_cancel(self, trade_id):
        if trade_id in self.trades:            
            self.trades[trade_id].status = 'cancel request'
    
    def amend_trade(self, trade_id, amend):
        if trade_id not in self.trades:
            raise ValueError('trade_id %i not found'%trade_id)
        contract, order = self.trades[trade_id] 
        if order.qty  * amend.qty < 0:
            raise ValueError('trade_id %i amend trading in opposite direction!'%trade_id)
        if abs(amend.qty) < order.filled:
            raise ValueError('trade_id %i Trying to amend a trade to %i but we already filled %i'%(trade_id, abs(amend.qty), order.filled))
        elif abs(amend.qty) == order.filled:
            order.status = 'done'
            order.qty = amend.qty
            return trade_id
        else:  
            order.status = 'done'
            
    
    def cancel_trade(self, trade_id):
        pass
    
    def trade_status(self, trade_id):
        pass
    
    def fill_trade(self, trade_id, fill):
        pass
            
    
    def cancel_request(self, order_id):
        if order_id in self.orders:            
            self.orders[order_id].status = 'cancel request'
        
    def archive(self, order_id = None, status = 'done'):
        """
        moves the orders from the working ones to the archive
        """
        if order_id is None:
            order_id = list(self.orders.keys())
        if isinstance(order_id, list):
            return type(order_id)([self.archive(o, status) for o in order_id])
        if order_id in self.orders:
            order = self.orders[order_id].copy()
            order.status = status
            self.archived_orders[order_id] = order
            self.archived_fills[order_id] = self.fills[order_id].copy()
            del self.orders[order_id]
            del self.fills[order_id]
        return order_id

    def cancel_order(self, order_id):
        return self.archive(order_id, 'cancelled')        

    def fill(self, fill):
        order_id = fill.order_id
        if order_id not in self.orders:
            fill.problem = 'order_id not found'
            self.bad_fills += fill
            return None
        else:
            order = self.orders[order_id]
        if order.open < fill.qty:
            fill.problem = 'fill qty %i exceeds amount working %i'%(fill.qty, order.open)
            self.bad_fills += fill
            return None
        self.fills[order_id] += fill
        fills = self.fills[order_id]
        order.open = order.open - fill.qty
        order.price = sum(fills[lambda price, qty: qty * price])/sum(fills.qty)
        if order.open == 0:
            self.archive(order_id, 'done')

    def order_status(self, order_id):
        if order_id in self.orders:
            return self.orders[order_id]
        elif order_id in self.archived_orders:
            return self.archived_orders[order_id]
        else:
            raise ValueError('order %i not found'%order_id)


    def _random_fill(self, order_id):
        """
        generates random fill
        """
        status = self.order_status(order_id)
        qty = max(1, status.open // 2)
        price = np.random.uniform(0,1)
        fill = Fill(order_id, qty, price)
        self.fill(fill)        

        