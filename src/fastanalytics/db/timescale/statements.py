from sqlalchemy import text

CREATE_HYPERTABLE_INTERVAL = text("""
SELECT hypertable_id, created FROM create_hypertable(
    :table_name,
    by_range(:time_column, INTERVAL :chunk_time_interval),
    if_not_exists => :if_not_exists,
    migrate_data => :migrate_data
);
""")


CREATE_HYPERTABLE_INTEGER = text("""
SELECT hypertable_id, created FROM create_hypertable(
    :table_name,
    by_range(:time_column, :chunk_time_interval),
    if_not_exists => :if_not_exists,
    migrate_data => :migrate_data
);
""")


AVAILABLE_HYPERTABLES = text("""
SELECT hypertable_schema
    ,hypertable_name
    ,owner
    ,num_dimensions
    ,num_chunks
    ,compression_enabled
    ,tablespaces
FROM timescaledb_information.hypertables;
""")
