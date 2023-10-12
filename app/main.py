import datetime, pytz
from typing import List, Annotated
from fastapi import FastAPI, HTTPException, Request, Response, status, Depends, Query
from pydantic import BaseModel, Field, ValidationError, validator

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse

import models.models as models
from databases.database import engine, sessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, not_, null, or_
import psycopg2

app = FastAPI(
    title="FastAPI App"
)
models.Base.metadata.create_all(bind=engine)

class CoilBase(BaseModel):
    length: int = Field(..., gt=0)
    weight: int = Field(..., gt=0)
    add_date: str = Field(None, max_length=11)
    delete_date: str = Field(None, max_length=11)
    
    @validator('add_date', 'delete_date')
    def validate_date_format(cls, date_string):
        if len(date_string) != 10:
            raise ValueError('Неверный формат даты. Используйте формат "yyyy-mm-dd".')
        try:
            datetime.datetime.strptime(date_string, '%Y%m%d')
        except ValueError:
            raise ValueError('Неверная дата.')
        return date_string

@app.exception_handler(psycopg2.DatabaseError)
async def handle_database_error(request, exc):
    # Обработка ошибки подключения к БД
    response = {"error": "Ошибка подключения к базе данных"}
    return JSONResponse(status_code=500, content=response)

@app.exception_handler(Exception)
async def handle_generic_error(request, exc):
    # Обработка других общих ошибок
    response = {"error": "Внутренняя ошибка сервера"}
    return JSONResponse(status_code=500, content=response)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        context=jsonable_encoder({'detail': exc.errors()})
    )

@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(response: Response, exc: ResponseValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        context=jsonable_encoder({'detail': exc.errors()})
    )

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        context=jsonable_encoder({'detail': exc.errors()})
    )

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post('/api/POST/')
async def post_coil(coil: CoilBase, db: db_dependency):
    tz = pytz.timezone('Europe/Moscow')  # Зону можно поменять или ставить просто системную
          
    today = datetime.datetime.now(tz).date()
    now_date = today.strftime("%Y-%m-%d")

    db_coils = models.Coil(length=coil.length, weight=coil.weight, add_date=now_date) # не написал delete_date
    db.add(db_coils)
    db.commit()
    db.refresh(db_coils)
    return {'id': db_coils.id}

@app.get('/api/GET/coil/{coil_id}')
async def set_coil(coil_id: int, db: db_dependency):
    result = db.query(models.Coil).filter(models.Coil.id == coil_id).first()
    print(db.query(models.Coil))
    if not result:
        raise HTTPException(status_code=404, detail="Coil is not found")
    return result

@app.get('/api/GET/coil/')
async def get_coils(
    db: db_dependency,
    start_id: int = Query(None, description="ID начального рулона"),
    end_id: int = Query(None, description="ID конечного рулона"),
    start_weight: float = Query(None, description="Начальный вес рулона"),
    end_weight: float = Query(None, description="Конечный вес рулона"),
    start_length: int = Query(None, description="Начальная длина рулона"),
    end_length: int = Query(None, description="Конечная длина рулона"),
    start_addition_date: datetime.date = Query(None, description="Начальная дата добавления на склад"),
    end_addition_date: datetime.date = Query(None, description="Конечная дата добавления на склад"),
    start_removal_date: datetime.date = Query(None, description="Начальная дата удаления со склада"),
    end_removal_date: datetime.date = Query(None, description="Конечная дата удаления со склада")):
    arr_req = []

    if start_id and end_id:
        arr_req.append(and_(models.Coil.id >= start_id, models.Coil.id <= end_id))
    if start_weight and end_weight:
        arr_req.append(and_(models.Coil.weight >= start_weight, models.Coil.weight <= end_weight))
    if start_length and end_length:
        arr_req.append(and_(models.Coil.length >= start_length, models.Coil.length <= end_length))
    if start_addition_date and end_addition_date:
        arr_req.append(and_(models.Coil.add_date >= start_addition_date, models.Coil.add_date <= end_addition_date))
    if start_removal_date and end_removal_date:
        arr_req.append(and_(models.Coil.delete_date >= start_removal_date, models.Coil.delete_date <= end_removal_date))
    
    result = db.query(models.Coil).filter(and_(i for i in arr_req)).all()
    
    return result

@app.get('/api/GET/coil/id/')
async def set_coil(min_id: int, max_id: int, db: db_dependency):
    if min_id and max_id:
        result = db.query(models.Coil).filter(and_(models.Coil.id >= min_id, models.Coil.id <= max_id)).all()

    print(db.query(models.Coil))
    if not result:
        raise HTTPException(status_code=404, detail="Coil is not found")
    return result

@app.get('/api/GET/coil/length/')
async def set_coil(min_length: int, max_length: int, db: db_dependency):
    if min_length and max_length:
        result = db.query(models.Coil).filter(and_(models.Coil.length >= min_length, models.Coil.length <= max_length)).all()
    
    print(db.query(models.Coil))
    if not result:
        raise HTTPException(status_code=404, detail="Coil is not found")
    return result

@app.get('/api/GET/coil/weight/')
async def set_coil(min_weight: int, max_weight: int, db: db_dependency):
    if min_weight and max_weight:
        result = db.query(models.Coil).filter(and_(models.Coil.weight >= min_weight, models.Coil.weight <= max_weight)).all()
    
    print(db.query(models.Coil))
    if not result:
        raise HTTPException(status_code=404, detail="Coil is not found")
    return result

@app.get('/api/GET/coil/add_date/')
async def set_coil(min_add_date: datetime.date, max_add_date: datetime.date, db: db_dependency):
    if min_add_date and max_add_date:
        result = db.query(models.Coil).filter(and_(models.Coil.add_date >= min_add_date, models.Coil.add_date <= max_add_date)).all()
    
    print(db.query(models.Coil))
    if not result:
        raise HTTPException(status_code=404, detail="Coil is not found")
    return result

@app.get('/api/GET/coil/delete_date/')
async def set_coil(min_delete_date: datetime.date, max_delete_date: datetime.date, db: db_dependency):
    if min_delete_date and max_delete_date:
        result = db.query(models.Coil).filter(and_(
            models.Coil.delete_date >= min_delete_date, 
            models.Coil.delete_date <= max_delete_date
            )).all()
    
    print(db.query(models.Coil))
    if not result:
        raise HTTPException(status_code=404, detail="Coil is not found")
    return result

# Статистика по рулонам на данном промежутке времени
@app.get('/api/GET/coil/stats/')
async def get_coil_stats(interval_start: datetime.date, interval_end: datetime.date, db: db_dependency):
    flag = or_(
        not_(
            and_(models.Coil.delete_date < interval_start, 
                 models.Coil.add_date < interval_end
                )
        ), 
        and_(models.Coil.delete_date.is_(None),
             interval_start <= models.Coil.add_date,
             interval_end >= models.Coil.add_date
            )
        )
    
    result = db.query(models.Coil).filter(flag)
    result = (result.all())

    resp = {}

    cnt_add = and_(models.Coil.add_date >= interval_start, interval_end >= models.Coil.add_date)
    res1 = db.query(models.Coil).filter(cnt_add).all()
    resp['added_count'] = len(res1)

    cnt_del = and_(not_(models.Coil.delete_date.is_(None)), models.Coil.delete_date >= interval_start, interval_end >= models.Coil.delete_date)
    res2 = db.query(models.Coil).filter(cnt_del).all()
    resp['deleted_count'] = len(res2)

    average_length = db.query(func.avg(models.Coil.length)).filter(flag).scalar()
    average_weight = db.query(func.avg(models.Coil.weight)).filter(flag).scalar()
    resp['avg_length'] = round(float(average_length), 4)
    resp['avg_weight'] = round(float(average_weight), 4)

    max_length = db.query(func.max(models.Coil.length)).filter(flag).scalar()
    max_weight = db.query(func.max(models.Coil.weight)).filter(flag).scalar()
    resp['max_length'] = round(float(max_length), 4)
    resp['max_weight'] = round(float(max_weight), 4)

    min_length = db.query(func.min(models.Coil.length)).filter(flag).scalar()
    min_weight = db.query(func.min(models.Coil.weight)).filter(flag).scalar()
    resp['min_length'] = round(float(min_length), 4)
    resp['min_weight'] = round(float(min_weight), 4)
    
    sum_weight = db.query(func.sum(models.Coil.weight)).filter(flag).scalar()
    resp['sum_weight'] = round(float(sum_weight), 4)

    max_interval = -1
    
    for curr in result:
        if curr.delete_date:
            date_end = curr.delete_date

            date_start = curr.add_date
    
            interval = (date_end - date_start)
            interval = interval.total_seconds()

            if max_interval == -1 or interval > max_interval:
                max_interval = interval
    if max_interval != -1:
        resp['max_interval_seconds'] = round(float(max_interval), 4)
    else:
        resp['max_interval'] = "There are no deleted coils in this interval"

    # Запрос для нахождения минимального количества рулонов
    min_coil_count = (
        db.query(func.count(models.Coil.id))
        .filter(models.Coil.add_date >= interval_start, models.Coil.add_date <= interval_end)
        .scalar()
    )
    
    # Запрос для нахождения максимального количества рулонов
    max_coil_count = (
        db.query(func.count(models.Coil.id))
        .filter(models.Coil.add_date >= interval_start, models.Coil.add_date <= interval_end)
        .scalar()
    )

    # Даты с минимальным и максимальным количеством рулонов
    min_coil_date = (
        db.query(models.Coil.add_date)
        .filter(models.Coil.add_date >= interval_start, models.Coil.add_date <= interval_end)
        .order_by(models.Coil.length.asc())
        .first()
        .add_date
    )

    max_coil_date = (
        db.query(models.Coil.add_date)
        .filter(models.Coil.add_date >= interval_start, models.Coil.add_date <= interval_end)
        .order_by(models.Coil.length.desc())
        .first()
        .add_date
    )
    resp["min_coil_count"] = {"date": min_coil_date, "count": min_coil_count}
    resp["max_coil_count"] = {"date": max_coil_date, "count": max_coil_count}

    min_weight_date = (
        db.query(models.Coil.add_date, func.sum(models.Coil.weight).label('total_weight'))
        .filter(models.Coil.add_date >= interval_start, models.Coil.add_date <= interval_end)
        .group_by(models.Coil.add_date)
        .order_by('total_weight')
        .first()
    )

    # Запрос для нахождения даты с максимальным суммарным весом
    max_weight_date = (
        db.query(models.Coil.add_date, func.sum(models.Coil.weight).label('total_weight'))
        .filter(models.Coil.add_date >= interval_start, models.Coil.add_date <= interval_end)
        .group_by(models.Coil.add_date)
        .order_by(func.sum(models.Coil.weight).desc())
        .first()
    )

    resp['summ_weight'] = {'min': min_weight_date, 'max': max_weight_date}
    
    return resp

@app.delete('/api/DELETE/coil/{coil_id}')
async def delete_coil(coil_id: int, db: db_dependency):
    result = db.query(models.Coil).filter(models.Coil.id == coil_id).first()
    # Проверка, что запись найдена
    if result:
        
        tz = pytz.timezone('Europe/Moscow')  # Зону можно поменять или ставить просто системную
          
        today = datetime.datetime.now(tz).date()
        now_date = today.strftime("%Y-%m-%d")
        result.delete_date = now_date

        # Сохранение изменений в базе данных
        db.commit()
        return {'id': coil_id}  
    else:
        # Обработка случая, когда запись не найдена
        raise HTTPException(status_code=404, detail="Coil is not found")

