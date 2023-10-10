## Данный проект представляет собой социальную сеть Yatube

Технологии:
  Django 2.2.16

в данном проекте была задача познакомиться с методикой тестирования и научиться
использвать Unittest в Django

Реализовано покрытие тестами приложения posts: 
  - протестированы модели приложения
  - реализована проверка namespace и шаблонов
  - реализована проверка views и form 

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Intemic/infra_sprint1.git
```

```
cd infra_sprint1
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

```
python3 manage.py migrate
```

Собрать frontend

```
cd frontend/ 
```
```
npm install
```
```
npm run build
```

Запустить проект:

```
python3 manage.py runserver
```
