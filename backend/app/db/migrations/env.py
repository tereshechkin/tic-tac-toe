import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from alembic import context
from sqlalchemy import create_engine

from app.db.base import Base
from app.config import settings
# Импорт моделей для регистрации в метаданных
from app.modules.idm import models  # noqa
from app.modules.game_repository import models  # noqa

target_metadata = Base.metadata


def run_migrations_offline():
    url = context.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # Используем синхронный URL (убираем asyncpg)
    sync_url = settings.DATABASE_URL.replace("+asyncpg", "")
    config = context.config
    config.set_main_option("sqlalchemy.url", sync_url)
    connectable = create_engine(config.get_main_option("sqlalchemy.url"))
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
