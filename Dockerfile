FROM python:3.7
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN  pip install rasa==2.1.0 \
 --use-feature=2020-resolver
RUN pip install -r requirements.txt
COPY . /code/
CMD python app.py
EXPOSE 5000