FROM python:3.11

WORKDIR /app

# copy the requirements file
COPY requirements.txt /app

# install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the application code
COPY . /app

# command to run the application
CMD ["python", "app.py"]
