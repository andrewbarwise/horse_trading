FROM python:3.11

WORKDIR /horse_trading

# Copy the requirements file
COPY horse_trading/requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY horse_trading .

# Command to run the application
CMD ["python", "app.py"]

