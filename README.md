# Запустить API

## Через Virtual Env

Перейти в папку app, открыть командную строку и написать 

1. `venv/Scripts/activate` - для активации виртуального окружения
2. `uvicorn main:app --reload` - для запуска сервера
Затем перейти по ссылке в консоли и дописать /docs для отображения документации и теста API

## Через Docker

Перейти в корневую папку с Dockerfile, открыть командную строку и написать 

1. `docker build . -t myimage_fastapi:latest` - создаем Docker-обрааз
   
2. `docker run -d -r 7330:8000 myimage_fastapi` - запускаем контейнер с сервером

_Вторая команда возвращает хэш, при помощи которого можно написать_

`docker logs code_hash`

_Выведет логи выполнения контейнера_

# Документация по API

Чтобы открыть документацию нужно прописать в браузере адрес `http://127.0.0.1:8000/docs`

# Прочее

По вопросам  писать на почту. Роут _/api/GET/coil/_ может принимать комбинированные и обычные диапазоны
