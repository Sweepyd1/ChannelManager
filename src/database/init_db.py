import asyncpg
from alembic.config import Config as AlembicConfig
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from loguru import logger
import asyncio

from ..config import cfg, project_root


async def create_db():
		db = await asyncpg.connect(
			host=cfg.postgresql.host,
			port=cfg.postgresql.port,
			user=cfg.postgresql.user,
			password=cfg.postgresql.password
		)
		
		existing_databases = await db.fetch("SELECT datname FROM pg_database WHERE datname = $1", cfg.postgresql.name)
		
		if not existing_databases:
			await db.execute(f"CREATE DATABASE \"{cfg.postgresql.name}\"")
			logger.success(f"Database '{cfg.postgresql.name}' created successfully.")
		else:
			logger.info(f"Database '{cfg.postgresql.name}' already exists.")

		await db.close()

def init_db() -> None:
	asyncio.run(create_db())

	config = AlembicConfig(project_root / 'alembic.ini')
	script = ScriptDirectory.from_config(config)
	head_revision = script.get_current_head()

	with EnvironmentContext(
		config,
		script,
		fn=lambda rev, _: script._upgrade_revs(head_revision, rev),
		as_sql=False,
		revision_environment=True,
		directives={},
	):
		script.run_env()