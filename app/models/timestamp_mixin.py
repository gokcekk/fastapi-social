# app/models/base.py

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, func

class TimestampMixin:
    """
    Common fields for all tables that include this mixin:
    * id: primary key
    * created_at: when the row was created
    * updated_at: when the row was last updated
    """

    # This class is a "mixin".
    # It is not a real table by itself.
    # It is meant to be inherited by other model classes
    # to add common columns to them.
    # Any model that inherits from TimestampMixin
    # will automatically have id, created_at and updated_at columns.


    # When the row was created (set by the database on insert)
    created_at = Column(
        DateTime(timezone=True),     # timezone=True: stores date and time with timezone information.
        server_default=func.now(),   # server_default=func.now(): when the row is first inserted,
                                     # the database automatically sets this field to the current time.
        nullable=False,              # nullable=False: this column cannot be null; every row must have a value.
    )

    # When the row was last updated (updated automatically on change)
    updated_at = Column(
        DateTime(timezone=True),     # Again, stores date and time with timezone information.
        server_default=func.now(),   # Initial value is set to "now" when the row is created.
        onupdate=func.now(),         # onupdate=func.now(): every time the row is updated,
                                     # the database automatically sets this field to the current time.
        nullable=False,              # This column also cannot be null.
    )
