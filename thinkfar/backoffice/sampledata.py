
from datetime import date

from thinkfar.inventory import User
from thinkfar.accounting import ItemClass


__copyright__ = 'Copyright (c) 2010-2011 Alessandro Amici. All rights reserved.'
__licence__ = 'GPLv3'


def init_sampledata():   
    me = User.get_by_key_name('alexamici')
    book = me.books.fetch(1)[0]
    car_class = ItemClass.get_by_key_name('GIFI/1740')
    car = car_class.create_itemset(book=book, uid='0123', name='My Car')
    car.description = 'A 2003 Honda'
    car.put()
    buy_a_car = car.item_class.transaction_template('buy')
    buy_a_car(car, date(2003, 2, 5), gross_price_paid=15000, taxes_paid=3500, resell_value=10000)
    sell_a_car = car.item_class.transaction_template('sell')
    sell_a_car.sell(car, date(2012, 5, 5), net_resell_value=3000, taxes_paid=50, fees_paid=250)

    shares_class = ItemClass.get_by_key_name('GIFI/3500')
    ge_plan = shares_class.create_itemset(book=book, uid='0124', name='GE shares')
    ge_plan.description = 'GE shares accumulation plan'
    ge_plan.put()
    # ge_plan.buy(start_date=date(2009, 12, 31), end_date=date(2010, 12, 31), amount=365, gross_price_paid=5530, commissions_paid=55)
    # ge_plan.sell(start_date=date(2029, 12, 31), end_date=date(2030, 12, 31), amount=365, net_resell_value=6880, taxes_paid=365, commissions_paid=55)
