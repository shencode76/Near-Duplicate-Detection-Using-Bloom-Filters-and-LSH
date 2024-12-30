# # Start from a base Python image
# FROM python:3.8-slim

# # Install Redis client
# RUN pip install redis
# RUN pip install flask

# # Set the working directory
# WORKDIR /app/src/a3

# # Set PYTHONPATH to include /app/src
# ENV PYTHONPATH=/app/src

# # Copy Python script and TSV files into the container
# COPY ./redis_data.py /app/src/a3/redis_data.py
# COPY data /app/src/a3/data


# # COPY ./src/a3/redis_data.py /app/src/a3/redis_data.py
# # COPY ./src/a3/data /app/src/a3/data


# # Expose the necessary port (for Redis or any API your app might expose)
# EXPOSE 5001

# # Set the command to run the Python script
# CMD ["python", "/app/src/a3/redis_data.py"]


# Start from a base Python image
FROM python:3.8-slim

# Install Redis client and Flask
RUN pip install redis
RUN pip install flask

# Set the working directory
WORKDIR /app/src

# Set PYTHONPATH to include /app/src
ENV PYTHONPATH=/app/src

# Copy Python script and TSV files into the container
# COPY ./src /app/src
RUN mkdir -p /app/src/a3/data

COPY ./src/a3/redis_data.py /app/src/a3/redis_data.py
COPY ./src/a3/data /app/src/a3/data

# Expose the necessary port
EXPOSE 5001

# Set the command to run the Python script
CMD ["python", "a3/redis_data.py"]
