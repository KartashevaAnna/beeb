from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker

from app.repositories.expenses import ExpensesRepo
from app.settings import ENGINE


def get_session() -> Session:
    session = sessionmaker(bind=ENGINE)
    try:
        yield (session := session())
    finally:
        session.close()


def expenses_repo(session: Session = Depends(get_session)) -> ExpensesRepo:
    return ExpensesRepo(session)
