import random

from app.models import Payment
from app.repositories.payments import PaymentRepo
from app.utils.constants import PRODUCTS


def test_payments_default_sorting(client, fill_db, category, session):
    """Case: normal mode.

    Checks that the latest added payment by default
    will be at the top of the list returned by the repository.
    """
    all_payments_before_adding = PaymentRepo(session).read_all()
    payment = Payment(
        name=random.choice(PRODUCTS),
        price=random.randrange(100, 5000, 100),
        category_id=category.id,
    )
    session.add(payment)
    session.flush()
    session.commit()
    session.expire_all()
    all_payments_after_adding = PaymentRepo(session).read_all()
    assert all_payments_before_adding[0] != all_payments_after_adding[0]
    assert payment.id == all_payments_after_adding[0].id
