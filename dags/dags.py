# import text and datetime libraty, we gonna use it for scheduling activities
import textwrap
from datetime import datetime, timedelta

# import DAG
from airflow.models.dag import DAG

# import operators package
from airflow.operators.python import PythonOperator

# import the function to be executed
from etl import extract, transform, load_csv
from db_load import load_sql


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
    extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract,
        dag=dag
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform,
        op_kwargs={'data': '{{ task_instance.xcom_pull(task_ids="extract_data") }}'},
        dag=dag
    )

    load_csv = PythonOperator(
        task_id='load_csv',
        python_callable=load_csv,
        op_kwargs={
            'data': '{{ task_instance.xcom_pull(task_ids="transform_data") }}',
            'filename': 'data.csv'
        },
        dag=dag
    )

    load_sql = PythonOperator(
        task_id='load_sql',
        python_callable=load_sql,
        dag=dag
    )


    # set the task dependencies
    extract >> transform >> load_csv >> load_sql