FROM public.ecr.aws/lambda/python:3.8

COPY requirements/prod.txt ${LAMBDA_TASK_ROOT}

RUN yum install -y postgresql-devel python-psycopg2 postgresql-libs

RUN python3 -m ensurepip
RUN pip install -r prod.txt

ADD src ${LAMBDA_TASK_ROOT}

CMD [ "main.handler" ]