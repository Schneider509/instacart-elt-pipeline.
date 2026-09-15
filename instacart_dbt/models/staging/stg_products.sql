with source as (

    select * from {{ source('instacart_raw', 'RAW_PRODUCTS') }}

),

renamed as (

    select
        cast(product_id as integer) as product_id,
        cast(product_name as varchar) as product_name,
        cast(aisle_id as integer) as aisle_id,
        cast(department_id as integer) as department_id
    from source

)

select * from renamed