"""Создание таблиц голосования.

Revision ID: 0f4cb7d03e8a
Revises:
Create Date: 2026-09-09 13:16:35

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0f4cb7d03e8a"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

poll_selection_type = sa.Enum("single", "multiple", name="poll_selection_type")


def upgrade() -> None:
    op.create_table(
        "polls",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column(
            "selection_type",
            poll_selection_type,
            nullable=False,
        ),
        sa.Column("min_selections", sa.Integer(), nullable=False),
        sa.Column("max_selections", sa.Integer(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "length(trim(question)) > 0",
            name="ck_polls_question_not_blank",
        ),
        sa.CheckConstraint(
            "min_selections > 0",
            name="ck_polls_min_selections_positive",
        ),
        sa.CheckConstraint(
            "max_selections > 0",
            name="ck_polls_max_selections_positive",
        ),
        sa.CheckConstraint(
            "min_selections <= max_selections",
            name="ck_polls_selection_range_valid",
        ),
        sa.CheckConstraint(
            "selection_type != 'single' OR "
            "(min_selections = 1 AND max_selections = 1)",
            name="ck_polls_single_selection_range",
        ),
        sa.CheckConstraint(
            "ends_at > starts_at",
            name="ck_polls_time_range_valid",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "poll_options",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("poll_id", sa.UUID(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "length(trim(text)) > 0",
            name="ck_poll_options_text_not_blank",
        ),
        sa.CheckConstraint(
            "position >= 0",
            name="ck_poll_options_position_non_negative",
        ),
        sa.ForeignKeyConstraint(["poll_id"], ["polls.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "poll_id",
            "position",
            name="uq_poll_options_poll_position",
        ),
    )
    op.create_index(
        "ix_poll_options_poll_id",
        "poll_options",
        ["poll_id"],
        unique=False,
    )

    op.create_table(
        "votes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("poll_id", sa.UUID(), nullable=False),
        sa.Column("participant_key_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "counted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "length(participant_key_hash) = 64",
            name="ck_votes_participant_key_hash_length",
        ),
        sa.ForeignKeyConstraint(["poll_id"], ["polls.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "poll_id",
            "participant_key_hash",
            name="uq_votes_poll_participant_key_hash",
        ),
    )
    op.create_index("ix_votes_poll_id", "votes", ["poll_id"], unique=False)

    op.create_table(
        "vote_selections",
        sa.Column("vote_id", sa.UUID(), nullable=False),
        sa.Column("option_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["option_id"],
            ["poll_options.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(["vote_id"], ["votes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("vote_id", "option_id"),
    )
    op.create_index(
        "ix_vote_selections_option_id",
        "vote_selections",
        ["option_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_vote_selections_option_id", table_name="vote_selections")
    op.drop_table("vote_selections")
    op.drop_index("ix_votes_poll_id", table_name="votes")
    op.drop_table("votes")
    op.drop_index("ix_poll_options_poll_id", table_name="poll_options")
    op.drop_table("poll_options")
    op.drop_table("polls")

    sa.Enum(name="poll_selection_type").drop(op.get_bind(), checkfirst=True)
