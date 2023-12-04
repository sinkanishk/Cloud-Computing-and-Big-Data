# Use an official Python runtime as a parent image
FROM python:3.9

# Copy the content of the project directory to the working directory
COPY . /app

# Set the working directory in the container
WORKDIR /app

# Install any dependencies
RUN pip install -r requirements.txt

# Specify the Flask environment port
ENV PORT 5000

# By default, listen on port 5000
EXPOSE 5000

# Set the directive to specify the executable that will run when the container is initiated
ENTRYPOINT [ "python" ]

# Specify the command to run on container start
CMD [ "app.py" ]
