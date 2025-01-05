FROM python:3.12

WORKDIR /app

# Install git and other dependencies
RUN pip install --upgrade pip


COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "codebot.wsgi:application", "-b", "0.0.0.0:8000"]