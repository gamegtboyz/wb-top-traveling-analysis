# import text and datetime libraty, we gonna use it for scheduling activities
import textwrap
from datetime import datetime, timedelta

# import DAG
from airflow.models.dag import DAG

# import operators package
from airflow.operators.python import PythonOperator

# import the function to be executed


# instantiate the DAG
with DAG(
    dag_id='wb-top-traveling-analysis',
    default_args={
        'depends_on_past': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    },
    schedule = timedelta(months=1),
    start_date = datetime(2025, 08, 1)
) as dag:
    
    # set the tasks list


    # set the task dependencies