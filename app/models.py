import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    MetaData,
    String,
    func,
    types,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class AlchemyBaseModel(DeclarativeBase):
    metadata = MetaData(schema="main")


class User(AlchemyBaseModel):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    password_hash_sum: Mapped[bytes] = mapped_column(
        LargeBinary, nullable=False
    )
    payments_list: Mapped[list["Payment"]] = relationship(
        back_populates="payment_user",
    )
    categories_list: Mapped[list["Category"]] = relationship(
        back_populates="category_user",
    )


class Category(AlchemyBaseModel):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    payments_list: Mapped[list["Payment"]] = relationship(
        back_populates="payment_category",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    category_user: Mapped["User"] = relationship(
        back_populates="categories_list",
    )


class Payment(AlchemyBaseModel):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[UUID] = mapped_column(
        types.UUID, nullable=False, unique=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    grams: Mapped[int] = mapped_column(
        BigInteger, nullable=True, doc="для расходов на еду"
    )
    quantity: Mapped[int] = mapped_column(
        BigInteger,
        nullable=True,
        doc="для расходов на непродовольственные товары",
    )
    amount: Mapped[int] = mapped_column(
        BigInteger, nullable=False, doc="стоимость"
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("category.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    payment_category: Mapped["Category"] = relationship(
        back_populates="payments_list",
    )
    payment_user: Mapped["User"] = relationship(
        back_populates="payments_list",
    )
