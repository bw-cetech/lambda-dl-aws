#Dockerfile - no changes just update to GitHub version control note
FROM public.ecr.aws/lambda/python:3.10
COPY . ${LAMBDA_TASK_ROOT}
COPY requirements.txt  .
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD ["main.handler"]
