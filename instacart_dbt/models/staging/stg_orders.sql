with source as (

    select * from {{ source('instacart_raw', 'RAW_ORDERS') }}

),

renamed as (

    select
        cast(order_id as integer) as order_id,
        cast(user_id as integer) as user_id,
        cast(order_number as integer) as order_number,
        cast(order_dow as integer) as order_day_of_week,
        cast(order_hour_of_day as integer) as order_hour_of_day,
        cast(days_since_prior_order as float) as days_since_prior_order
    from source

)

select * from renamed