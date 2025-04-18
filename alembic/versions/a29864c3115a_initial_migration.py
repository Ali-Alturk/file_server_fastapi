"""Initial migration

Revision ID: a29864c3115a
Revises: 491008a78947
Create Date: 2025-03-29 12:56:35.214501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'a29864c3115a'
down_revision: Union[str, None] = '491008a78947'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_task_statuses_id', table_name='task_statuses')
    op.drop_index('task_id', table_name='task_statuses')
    op.drop_table('task_statuses')
    op.drop_table('file_uploads')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file_uploads',
    sa.Column('file_hash', mysql.VARCHAR(length=64), nullable=False),
    sa.Column('original_filename', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('file_path', mysql.VARCHAR(length=512), nullable=True),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('status', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.Column('is_deleted', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='file_uploads_ibfk_1'),
    sa.PrimaryKeyConstraint('file_hash'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('task_statuses',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('task_id', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('status', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.Column('updated_at', mysql.DATETIME(), nullable=True),
    sa.Column('result', mysql.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('task_id', 'task_statuses', ['task_id'], unique=True)
    op.create_index('ix_task_statuses_id', 'task_statuses', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=150), nullable=True),
    sa.Column('email', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('hashed_password', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('is_staff', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('created_at', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    # ### end Alembic commands ###