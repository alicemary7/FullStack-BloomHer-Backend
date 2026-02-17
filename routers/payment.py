from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from dependencies import connect_db
from models.payment import Payment
from models.order import Order
from schemas.payment import PaymentCreate, PaymentOut

payment_router = APIRouter(prefix="/payments", tags=["Payments"])


@payment_router.post(
    "/", response_model=PaymentOut, status_code=status.HTTP_201_CREATED
)
def make_payment(payment_data: PaymentCreate, db: Session = Depends(connect_db)):

    order = db.query(Order).filter(Order.id == payment_data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    existing_payment = db.query(Payment).filter(Payment.order_id == order.id).first()
    if existing_payment:
        raise HTTPException(status_code=400, detail="Order already paid")

    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method=payment_data.payment_method,
        status="completed",
    )
    db.add(payment)

    order.status = "paid"

    db.commit()
    db.refresh(payment)
    db.refresh(order)

    return payment

@payment_router.get("/{payment_id}", response_model=PaymentOut)
def get_payment_by_id(
    payment_id: int,
    db: Session = Depends(connect_db)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment

