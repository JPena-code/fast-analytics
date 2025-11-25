import sqlalchemy
from sqlalchemy import Connection


def activate_ext(conn: Connection, ext: str) -> None:
    """Activate an extension in the database.
    Args:
        conn (Connection): `sqlalchemy.Connection` connection to the database
        ext (str): The name of the extension to activate
    """
    name = conn.execute(
        sqlalchemy.text("SELECT name FROM pg_available_extensions WHERE name = :ext").bindparams(
            ext=ext
        )
    ).scalar()
    if name is None:
        raise ValueError(f'Extension "{ext}" is not available in the database.')

    conn.execute(sqlalchemy.text(f'CREATE EXTENSION IF NOT EXISTS "{name}"'))
