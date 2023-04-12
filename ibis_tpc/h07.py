"Volume Shipping Query (Q7)"

import ibis


def tpc_h07(con, NATION1="FRANCE", NATION2="GERMANY", DATE="1995-01-01"):
    supplier = con.table("supplier")
    lineitem = con.table("lineitem")
    orders = con.table("orders")
    customer = con.table("customer")
    nation = con.table("nation")

    q = supplier
    q = q.join(lineitem, supplier.s_suppkey == lineitem.l_suppkey)
    q = q.join(orders, orders.o_orderkey == lineitem.l_orderkey)
    q = q.join(customer, customer.c_custkey == orders.o_custkey)
    n1 = nation
    n2 = nation.view()
    q = q.join(n1, supplier.s_nationkey == n1.n_nationkey)
    q = q.join(n2, customer.c_nationkey == n2.n_nationkey)

    q = q[
        n1.n_name.name("supp_nation"),
        n2.n_name.name("cust_nation"),
        lineitem.l_shipdate,
        lineitem.l_extendedprice,
        lineitem.l_discount,
        lineitem.l_shipdate.year().cast("string").name("l_year"),
        (lineitem.l_extendedprice * (1 - lineitem.l_discount)).name("volume"),
    ]

    q = q.filter(
        [
            ((q.cust_nation == NATION1) & (q.supp_nation == NATION2))
            | ((q.cust_nation == NATION2) & (q.supp_nation == NATION1)),
            q.l_shipdate.cast("date").between(ibis.date(DATE), ibis.date(DATE)
            + ibis.interval(years=2) - ibis.interval(days=1)),
        ]
    )

    gq = q.group_by(["supp_nation", "cust_nation", "l_year"])
    q = gq.aggregate(revenue=q.volume.sum())
    q = q.order_by(["supp_nation", "cust_nation", "l_year"])

    return q
