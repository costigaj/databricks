#Catalog federation test
spark.sql("USE CATALOG oracle_postgres_catalog")
spark.sql("USE SCHEMA public")

# 1. Inspect the orders table
orders_df = spark.sql("""
    SELECT
        orders.order_id,
        orders.customer_id,
        orders.product_id,
        orders.quantity,
        orders.order_date,
        orders.order_status
    FROM oracle_postgres_catalog.public.orders AS orders
    ORDER BY orders.order_id
""")
orders_df.show(truncate=False)

# 2. Join orders, customers, and products to calculate line totals
order_summary_df = spark.sql("""
    SELECT
        orders.order_id,
        orders.order_date,
        customers.full_name,
        customers.region,
        products.product_name,
        products.category,
        orders.quantity,
        products.unit_price,
        orders.quantity * products.unit_price AS line_total,
        orders.order_status
    FROM oracle_postgres_catalog.public.orders AS orders
    INNER JOIN oracle_postgres_catalog.public.customers AS customers
        ON orders.customer_id = customers.customer_id
    INNER JOIN oracle_postgres_catalog.public.products AS products
        ON orders.product_id = products.product_id
    WHERE orders.order_status IN ('Completed', 'Shipped')
    ORDER BY orders.order_id
""")
