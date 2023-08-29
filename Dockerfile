
FROM python:3.9   

ENV AppHOME=/home/airport/

RUN mkdir -p $AppHOME  

WORKDIR $AppHOME  

RUN pip install --upgrade pip  

COPY airport/  $AppHOME
COPY requirements.txt $AppHOME

RUN pip install -r requirements.txt  

EXPOSE 8000  

RUN python manage.py migrate

RUN pip freeze > docker_req_versions.txt

CMD python manage.py runserver  0.0.0.0:8000
