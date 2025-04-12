import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, MetaData, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class AlchemyBaseModel(DeclarativeBase):
    metadata = MetaData(schema="main")


class Category(AlchemyBaseModel):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    expense_list: Mapped[list["Expense"]] = relationship(
        back_populates="expense_category",
    )


class Expense(AlchemyBaseModel):
    __tablename__ = "expenses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("category.id"), nullable=False
    )
    expense_category: Mapped["Category"] = relationship(
        back_populates="expense_list",
    )
