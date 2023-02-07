import sqlite3


class Database:
    def __init__(self, file):
        self.con = sqlite3.connect(database=file, timeout=10)
        self.cur = self.con.cursor()
        print("[DataBase] Inited")

    def get_items(self):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `items`").fetchall()
            return r

    def get_milks(self):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `milks`").fetchall()
            return r

    def get_milk(self, id):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `milks` WHERE id = ?", (id,)).fetchone()
            return r

    def get_sizes(self):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `sizes`").fetchall()
            return r

    def get_size(self, id):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `sizes` WHERE id = ?", (id,)).fetchone()
            return r

    def get_item(self, id):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `items` WHERE id = ?", (id,)).fetchone()
            return r
    def get_order_payed(self, user):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `orders` WHERE user = ? AND status = ? ORDER BY time DESC", (user,'payed',)).fetchone()
            return r
    def get_item_name(self, name):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `items` WHERE name = ?", (name,)).fetchone()
            return r

    def add_item_orders(self, msg, id, user):
        with self.con:
            self.cur.execute(
                f"INSERT INTO orders (`user`, `msg`, `itemid`, `status`) VALUES ('{user}', '{msg}', '{id}', 'wait')")

    def exists_order(self, id, user):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `orders` WHERE user = ? AND itemid = ? AND status = ?",
                                 (user, id, 'wait')).fetchone()
            if r is None:
                return False
            else:
                return True

    def get_order(self, id, user, status):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `orders` WHERE user = ? AND itemid = ? AND status = ?",
                                 (user, id, status)).fetchone()
            return r

    def get_order_user(self, user, status):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `orders` WHERE user = ? AND status = ?",
                                 (user, status)).fetchone()
            return r

    def delete_order(self, user):
        with self.con:
            r = self.cur.execute("DELETE FROM orders WHERE status = ? AND user = ?", ('wait', user))

    def set_order_milk(self, user, item, milk):
        with self.con:
            r = self.cur.execute("UPDATE orders SET milk = ? WHERE user = ? AND itemid = ? AND status = ?",
                                 (milk, user, item, 'wait'))

    def set_order_size(self, user, item, size):
        with self.con:
            r = self.cur.execute("UPDATE orders SET size = ? WHERE user = ? AND itemid = ? AND status = ?",
                                 (size, user, item, 'wait'))

    def set_comment(self, user, comment):
        with self.con:
            r = self.cur.execute("UPDATE orders SET comment = ? WHERE user = ? AND status = ?", (comment, user, 'wait'))

    def exists_user(self, user):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `users` WHERE user = ?",
                                 (user,)).fetchone()
            if r is None:
                return False
            else:
                return True

    def add_user(self, user):
        with self.con:
            self.cur.execute(
                f"INSERT INTO users (`user`) VALUES ('{user}')")

    def get_user(self, user):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `users` WHERE user = ?",
                                 (user,)).fetchone()
            return r

    def get_admins_limit(self, page):
        with self.con:
            start = page * 10 - 10
            end = page * 10
            r = self.cur.execute(f"SELECT * FROM `users` WHERE is_admin = ? LIMIT ? OFFSET ?",
                                 (1, end, start,)).fetchall()
            return r



    def get_users_limit(self, page):
        with self.con:
            start = page * 10 - 10
            end = page * 10
            r = self.cur.execute(f"SELECT * FROM `users` LIMIT ? OFFSET ?",
                                 (end, start,)).fetchall()
            return r

    def get_admins(self):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `users` WHERE is_admin = ?",
                                 (1,)).fetchall()
            return r

    def get_staff(self):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `users` WHERE is_staff = ?",
                                 (1,)).fetchall()
            return r

    def get_users(self):
        with self.con:
            r = self.cur.execute(f"SELECT * FROM `users`").fetchall()
            return r

    def is_admin(self, user):
        with self.con:
            if not self.exists_user(user):
                return False
            r = self.cur.execute(f"SELECT is_admin FROM `users` WHERE user = ?",
                                 (user,)).fetchone()
            if r[0] == 0:
                return False
            else:
                return True

    def user_set_admin(self, user, value):
        with self.con:
            r = self.cur.execute(f"UPDATE users SET `is_admin` = ? WHERE user = ?",
                                 (value, user,))

    def delete_user(self, user, confirm):
        with self.con:
            if confirm == 1:
                r = self.cur.execute(f"DELETE FROM users WHERE user = ?",
                                     (user,))
    def delete_item(self, item):
        with self.con:
            r = self.cur.execute(f"DELETE FROM items WHERE id = ?",
                                   (item,))
    def create_item(self, name):
        with self.con:
            self.cur.execute(
                f"INSERT INTO items (`name`, `show`) VALUES ('{name}','0')")
            return name

    def set_description(self, name, desc):
        with self.con:
            r = self.cur.execute(f"UPDATE items SET `description` = ? WHERE name = ? AND show = ?",
                                 (name, desc, 0,))

    def set_price(self, name, price: int = 100):
        with self.con:
            r = self.cur.execute(f"UPDATE items SET `price` = ? WHERE name = ? AND show = ?",
                                 (name, price, 0,))

    def set_show(self, name):
        with self.con:
            r = self.cur.execute(f"UPDATE items SET `show` = ? WHERE name = ? AND show = ?",
                                 (1, name, 0,))

    def set_name(self, name,user):
        with self.con:
            r = self.cur.execute(f"UPDATE items SET `name` = ? WHERE name = ? AND show = ?",
                                 (1, name, 0,))
            self.set_itemname(name,user)
    def set_itemname(self, name,user):
        with self.con:
            r = self.cur.execute(f"UPDATE users SET `itemname` = ? WHERE user = ?",
                                 (name, user,))

    def get_items_limit(self,page):
        with self.con:
            start = page * 10 - 10
            end = page * 10
            r = self.cur.execute(f"SELECT * FROM `items` LIMIT ? OFFSET ?",
                                 (end, start,)).fetchall()
            return r
    def set_order_status(self,user,status,new_status,time):
        with self.con:
            r = self.cur.execute(f"UPDATE orders SET `status` = ?, `time` = ? WHERE status = ? AND `user` = ?",
                                 (new_status, time,status,user,))