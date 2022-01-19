from pyg_base import named_dict, is_int

__all__ = ['Order', 'Fill', 'Trade']


BUY = 1
SELL = -1

_order_type  = 'order_type'
_market = 'market'
_limit = 'limit'

_sides = {BUY : BUY,   'BUY': BUY,  'B': BUY,   'buy': BUY,  'Buy' : BUY,  'b': BUY,  'long' : BUY, 
          SELL: SELL, 'SELL': SELL, 'S': SELL, 'sell': SELL, 'Sell': SELL, 's': SELL, 'short': SELL}

def as_side(side):
    if side not in _sides:
        raise ValueError('side of trade %s not understood'%side)
    return _sides[side]

def is_qty(qty):
    return is_int(qty) and qty>=0

def as_params(params):
    if params is None:
        params = {}
    if not isinstance(params, dict):
        raise ValueError('cannot convert params')
    if _order_type not in params:
        if _limit in params:
            params[_order_type] = _limit
        else:
            params[_order_type] = _market
    if params[_order_type] == _limit and _limit not in params:
        raise ValueError('limit order requested but no limit price provided')
    return params

Order = named_dict('Order', ['qty', 'side', 'params'],  
                   defaults = dict(params = None),
                   types = dict(qty = 'pyg_oms._order.is_qty'), 
                   casts = dict(params = 'pyg_oms._order.as_params', 
                                side = 'pyg_oms._order.as_side'))


Fill = named_dict('Fill', ['trade_id', 'qty', 'price', 'date'], 
                      defaults = dict(date = None),
                      types = dict(date = 'pyg_base.is_date', 
                                   qty = 'pyg_oms._order.is_qty', 
                                   price = 'pyg_base.is_num'),
                      casts = dict(date = 'pyg_base.dt', 
                                   price = 'pyg_base.as_float'))


Trade = named_dict('Trade', ['contract', 'order', 'broker_id', 'fills'], 
                      defaults = dict(fills = {}, broker_id =  None),
                   )

