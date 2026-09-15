with source as (

    select * from {{ source('instacart_raw', 'RAW_AISLES') }}

),

renamed as (

    select
        cast(aisle_id as integer) as aisle_id,
        cast(aisle as varchar) as aisle_name
    from source

)

select * from renamed