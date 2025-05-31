FROM python:3.10-slim

WORKDIR /
# Copy requirements first to leverage Docker cache
COPY requirements.txt /
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your handler file
COPY rp_handler.py /
COPY dia/ /dia/

# Start the container
CMD ["python3", "-u", "rp_handler.py"] 