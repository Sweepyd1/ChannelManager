"""init_migration

Revision ID: bfbf53dc0b61
Revises: 
Create Date: 2025-02-08 20:15:19.696892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfbf53dc0b61'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.BIGINT(), nullable=False, comment='Идентификатор пользователя в Telegram'),
    sa.PrimaryKeyConstraint('id'),
    comment='Пользователи телеграм бота'
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('channel_groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('user_id', sa.BIGINT(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    comment='Группы каналов для массовой рассылки'
    )
    op.create_table('posts',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('content', sa.JSON(), nullable=False, comment="Структура: {'text': str, 'media': list, 'buttons': list}"),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('user_id', sa.BIGINT(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('scheduled_time', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    comment='Посты для рассылки по каналам'
    )
    op.create_table('channels',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('telegram_chat_id', sa.BIGINT(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.BIGINT(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('added_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['channel_groups.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('telegram_chat_id'),
    comment='Телеграм каналы для рассылки'
    )
    op.create_index('idx_telegram_chat_id', 'channels', ['telegram_chat_id'], unique=True)
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.UUID(), nullable=False),
    sa.Column('channel_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('sent_at', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('error_message', sa.TEXT(), nullable=True),
    sa.Column('message_id', sa.BIGINT(), nullable=True),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id'),
    comment='Задачи на отправку постов в каналы'
    )
    op.create_index('idx_task_status', 'tasks', ['status'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_task_status', table_name='tasks')
    op.drop_table('tasks')
    op.drop_index('idx_telegram_chat_id', table_name='channels')
    op.drop_table('channels')
    op.drop_table('posts')
    op.drop_table('channel_groups')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
