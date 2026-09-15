with orders as (

    select * from {{ ref('stg_orders') }}

),

order_items as (

    select * from {{ ref('stg_order_products') }}

),

order_summary as (

    select
        order_id,
        count(product_id) as total_products,
        sum(is_reordered) as total_reordered_products
    from order_items
    group by order_id

)

select
    orders.order_id,
    orders.user_id,
    orders.order_number,
    orders.order_day_of_week,
    orders.order_hour_of_day,
    orders.days_since_prior_order,
    coalesce(order_summary.total_products, 0) as total_products,
    coalesce(order_summary.total_reordered_products, 0) as total_reordered_products
from orders
left join order_summary on orders.order_id = order_summary.order_id