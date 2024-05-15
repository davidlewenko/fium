# Use an official Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.9

# Install system dependencies required for OpenCV
RUN yum install -y mesa-libGL

COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src/* ${LAMBDA_TASK_ROOT}

CMD [ "main.handler" ]
