from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from settings.database import Base


class SelectionType(PyEnum):
    SINGLE = "single"
    MULTIPLE = "multiple"

    def __str__(self) -> str:
        return self.value


selection_type_enum = SQLEnum(
    SelectionType,
    name="poll_selection_type",
    values_callable=lambda enum: [item.value for item in enum],
)


class Poll(Base):
    __tablename__ = "polls"
    __table_args__ = (
        CheckConstraint("length(trim(question)) > 0", name="ck_polls_question_not_blank"),
        CheckConstraint("min_selections > 0", name="ck_polls_min_selections_positive"),
        CheckConstraint("max_selections > 0", name="ck_polls_max_selections_positive"),
        CheckConstraint(
            "min_selections <= max_selections",
            name="ck_polls_selection_range_valid",
        ),
        CheckConstraint(
            "selection_type != 'single' OR "
            "(min_selections = 1 AND max_selections = 1)",
            name="ck_polls_single_selection_range",
        ),
        CheckConstraint("ends_at > starts_at", name="ck_polls_time_range_valid"),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    selection_type: Mapped[SelectionType] = mapped_column(
        selection_type_enum,
        nullable=False,
    )
    min_selections: Mapped[int] = mapped_column(Integer, nullable=False)
    max_selections: Mapped[int] = mapped_column(Integer, nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    options: Mapped[list[PollOption]] = relationship(
        back_populates="poll",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="PollOption.position",
    )


class PollOption(Base):
    __tablename__ = "poll_options"
    __table_args__ = (
        UniqueConstraint("poll_id", "position", name="uq_poll_options_poll_position"),
        CheckConstraint("length(trim(text)) > 0", name="ck_poll_options_text_not_blank"),
        CheckConstraint("position >= 0", name="ck_poll_options_position_non_negative"),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    poll_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("polls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    poll: Mapped[Poll] = relationship(back_populates="options", lazy="select")


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint(
            "poll_id",
            "participant_key_hash",
            name="uq_votes_poll_participant_key_hash",
        ),
        CheckConstraint(
            "length(participant_key_hash) = 64",
            name="ck_votes_participant_key_hash_length",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    poll_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("polls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    participant_key_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    counted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    selections: Mapped[list[VoteSelection]] = relationship(
        back_populates="vote",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class VoteSelection(Base):
    __tablename__ = "vote_selections"

    vote_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("votes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    option_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey("poll_options.id", ondelete="RESTRICT"),
        primary_key=True,
        index=True,
    )

    vote: Mapped[Vote] = relationship(back_populates="selections", lazy="joined")
