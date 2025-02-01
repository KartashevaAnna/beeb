from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker

from app.repositories.expenses import ExpenseRepo
from app.settings import ENGINE


def get_session() -> Session:
    session = sessionmaker(autocommit=False, expire_on_commit=True, bind=ENGINE)
    try:
        yield (session := session())
    finally:
        session.close()


def expenses_repo(session: Session = Depends(get_session)) -> ExpenseRepo:
    return ExpenseRepo(session)
