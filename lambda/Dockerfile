# AWS Lambda Container Image for Rent Prediction Inference
# Base image: Official AWS Lambda Python 3.12 Runtime
FROM public.ecr.aws/lambda/python:3.12

# Set working directory to Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}

# Install minimal ML inference dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy handler and serialized model artifacts
COPY lambda_function.py .
COPY models/ ./models/

# Command handler for AWS Lambda invocation
CMD ["lambda_function.lambda_handler"]
