from fastapi import FastAPI, Depends, HTTPException
import models                  
from database import engine, SessionLocal     
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from auth import get_current_user, get_user_exception

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Order(BaseModel):
    address: str
    description: Optional[str]
    complete: bool=False
    status: str="Incomming order...."

@app.post("/api/order")
async def create_order(order: Order, 
                        user: dict = Depends(get_current_user),
                        db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    order_model = models.Orders()
    order_model.address = order.address
    order_model.description = order.description
    order_model.complete = order.complete
    order_model.status = order.status
    order_model.owner_id = user.get("id")

    db.add(order_model)
    db.commit()

    return successful_response(201)

@app.put("/api/order/update/{order_id}")
async def update_order(order_id: int,
                         order: Order, 
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    order_model = db.query(models.Orders)\
        .filter(models.Orders.id == order_id)\
        .filter(models.Orders.owner_id == user.get("id"))\
        .first()
    if order_model is None:
        raise http_exception()

    order_model.address = order.address
    order_model.description = order.description
    order_model.complete = order.complete
    order_model.status = order.status

    db.add(order_model)
    db.commit()

    return successful_response(200)

@app.put("/api/order/status/{order_id}")
async def update_status(order_id: int,
                         order: Order, 
                         user: dict = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    order_model = db.query(models.Orders)\
        .filter(models.Orders.id == order_id)\
        .filter(models.Orders.owner_id == user.get("id"))\
        .first()
    if order_model is None:
        raise http_exception()

    order_model.status = order.status

    db.add(order_model)
    db.commit()

    return successful_response(200)

@app.delete("/api/order/delete/{order_id}")
async def delete_order(order_id: int,
                     user: dict = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()                 
    order_model = db.query(models.Orders)\
        .filter(models.Orders.id == order_id)\
        .filter(models.Orders.owner_id == user.get("id"))\
        .first()
    if order_model is None:
        raise http_exception()
    
    db.query(models.Orders)\
        .filter(models.Orders.id == order_id)\
        .delete()

    db.commit()

    return successful_response(200)

@app.get("/api/user/orders/")
async def get_users_orders(db: Session = Depends(get_db)):
    return db.query(models.Orders).all()

#@app.get("/todos/user")
#async def read_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
#    if user is None:
#        raise get_user_exception()
#    return db.query(models.Orders).filter(models.Orders.owner_id == user.get("id")).all()
#    
#@app.get("/todo/{todo_id}")
#async def read_todo(todo_id: int,
#                    user:dict = Depends(get_current_user),
#                     db: Session = Depends(get_db)):
#    if user is None:
#        raise get_user_exception()
#    todo_model = db.query(models.Orders)\
#        .filter(models.Orders.id == todo_id)\
#        .filter(models.Orders.owner_id == user.get("id"))\
#        .first()
#    if todo_model is not None:
#        return todo_model
#    raise http_exception()

def successful_response(status_code: int):
    return {
        'status': status_code,
        'transaction': 'Successful'
    }

def http_exception():
    return HTTPException(status_code=404, detail="Todo not found")

