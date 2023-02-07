from database import Database

db = Database("db.db")


class Core:
    def __init__(self):
        pass

    def calc_price(self, user):
        order = db.get_order_user(user, 'wait')
        milk = db.get_milk(order[6])
        size = db.get_size(order[5])
        print(milk,size)
        order_price = db.get_item(order[4])[4]
        price = order_price + size[3] + milk[3]
        res = {"drink": {"price": order_price},
               "milk": {"price": milk[3], "name": milk[1]},
               "size": {"price": size[3], "name": size[1], "ml": size[2]},
               "total": {'price': price}
               }
        print(res)
        return res
    def calc_price_order(self, order):
        milk = db.get_milk(order[6])
        size = db.get_size(order[5])
        print(milk,size)
        order_price = db.get_item(order[4])[4]
        price = order_price + size[3] + milk[3]
        res = {"drink": {"price": order_price},
               "milk": {"price": milk[3], "name": milk[1]},
               "size": {"price": size[3], "name": size[1], "ml": size[2]},
               "total": {'price': price}
               }
        print(res)
        return res
