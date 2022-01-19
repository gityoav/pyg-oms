from pyg_base import dictattr
from pyg_oms._order import Order, Trade, Fill
from pyg_oms._broker import Broker

class EMS(Broker):
    """    
    The execution management service:
    2) receives orders and sends them to the market. 
    3) receives fills from the market and assigns them back to each order    
    """

    def __init__(self, brokers = {}):
        self.brokers = brokers
        self.broker_trades = {} ## our trades are stored as (broker_id, trade_id) from each broker
        self.trades = {} ## a mapping from trade_id to the set of brokers we got the trade_id from
    
    def send_trade(self, contract, order, broker_id = None):
        if broker_id is None:            
            broker_id = broker_id or self.find_best_broker(contract, order)
            broker = self.brokers[broker_id]
        else:
            broker = self.brokers[broker_id]
            if not broker.pre_trade_check():
                raise ValueError('Broker %s refuses to execute')
        trade_id = broker.send_trade(contract, order)
        trade = Trade(contract = contract, order = order, broker_id = broker_id)
        _id = (broker_id, trade_id)        
        self.broker_trades[_id] = trade
        self.trades[trade_id] = self.trades.get(trade_id, set()) | set([broker_id])
        return _id

    def find_best_broker(self, contract, order):
        """
        decide on the best broker to exercise. We implement the most basic, cost-based sorting initially
        """
        brokers = [broker_id for broker_id, broker in self.brokers.items() if broker.pre_trade_check(contract, order)]
        if len(brokers) == 1:
            return brokers[0]
        elif len(brokers) == 0:
            raise ValueError('no broker found that can handle order %s %s'%(contract, order))
        else:
            costs = sorted([(self.brokers[broker_id].trade_cost(contract, order), broker_id) for broker_id in brokers]) # find cost for each broker, execute with cheapest one...
            return costs[0][1]
        
    def get_broker_and_trade_id(self, trade_id):
        if isinstance(trade_id, tuple) and len(trade_id) == 2:
            return trade_id
        elif trade_id in self.trades:
            brokers = self.trades[trade_id]
            if len(brokers) == 1:
                return list(brokers)[0], trade_id
            else:
                raise ValueError('more than one broker %s match trade %i'%(brokers, trade_id))
        else:
            raise ValueError('trade id %s not found'%trade_id)

    def request_cancel(self, trade_id):
        bid, tid = self.get_broker_and_trade_id(trade_id)
        return self.brokers[bid].request_cancel(tid)
            
    
    def amend_trade(self, trade_id, amend):
        bid, tid = self.get_broker_and_trade_id(trade_id)
        return self.brokers[bid].amend_trade(tid, amend)
    
    def cancel_trade(self, trade_id):
        bid, tid = self.get_broker_and_trade_id(trade_id)
        return self.brokers[bid].cancel_trade(tid)
    
    def trade_status(self, trade_id):
        bid, tid = self.get_broker_and_trade_id(trade_id)
        return self.brokers[bid].trade_status(tid)
    
    def fill_trade(self, trade_id, fill):
        bid, tid = self.get_broker_and_trade_id(trade_id)
        return self.brokers[bid].fill_trade(tid, fill)

    def pre_trade_check(self, contract, order):
        return max([broker.pre_trade_check(contract, order) for broker in self.brokers.values()])

    def trade_cost(self, contract, order):
        return min([broker.trade_cost(contract, order) for broker in self.brokers.values()])
        


    b = DummyBroker()
    order_id = b.send_order(Order('TY', 10))
    order_id = b.send_order(Order('ES', 10))
    for i in range(10):
        if b.orders:
            ids = list(b.orders.keys())
            for order_id in ids:
                b._random_fill(order_id)
            print(b.orders)
            print('--------')

    b.archived_fills[1]
    b.archived_orders[1]    
