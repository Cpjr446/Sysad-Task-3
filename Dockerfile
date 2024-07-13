# Use the official Python image
FROM python:latest

# Set the working directory
WORKDIR /home/Sysad/task3

# Copy the current directory contents into the container
COPY . .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the wait-for-it script
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Run the server
CMD ["/wait-for-it.sh", "db:3306", "--", "python", "server.py"]
