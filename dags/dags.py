# import text and datetime libraty, we gonna use it for scheduling activities
import textwrap
from datetime import datetime, timedelta

# import DAG
from airflow.models.dag import DAG

# import operators package
from airflow.operators.python import PythonOperator

# import the function to be executed
from etl import extract_transform_load
from db_load import load_sql


# instantiate the DAG
with DAG(
    dag_id='wb-top-traveling-analysis',
    default_args={
        'depends_on_past': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
    },
    schedule = timedelta(days=30),
    start_date = datetime(2025, 8, 1)
) as dag:
    
    # set the tasks list
    extract_transform_load = PythonOperator(
        task_id='extract_transform_load',
        python_callable=extract_transform_load,
        dag=dag
    )

    load_sql = PythonOperator(
        task_id='load_sql',
        python_callable=load_sql,
        dag=dag
    )
    
    # set the task dependencies
    extract_transform_load >> load_sql