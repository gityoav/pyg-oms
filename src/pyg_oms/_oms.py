class OMS():
    """
    An OMS is responsible of
    1) need to be stateless!! i.e. needs to be able to restart safely
    2) find out required positions from multiple users
    3) aggregate into a single target order
    4) route trade to the EMS
    
    """
    
    def __init__(self, brokers, position_db, orders_db, fills_db, clients_db):
        self.pdb = position_db
        self.odb = orders_db
        self.fdb = fills_db
        self.cdb = clients_db
        
    

