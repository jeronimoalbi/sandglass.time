from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from sandglass.time.models import META
from sandglass.time.models import scan_models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
CONFIG = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(CONFIG.config_file_name)

# Register models so they are available in META
scan_models('sandglass.time.models')


def run_migrations_offline():
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = CONFIG.get_main_option("sqlalchemy.url")
    context.configure(url=url)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = engine_from_config(
        CONFIG.get_section(CONFIG.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )
    connection = engine.connect()
    context.configure(connection=connection, target_metadata=META)

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
