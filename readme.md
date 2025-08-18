# Historical Trends of Tourism Analysis
This project is the simple project built as a showcase of ETL process and pipelines building, then we will use those data to perform an analytical review, then visualize them through common BI tools -- We gonna use PowerBI in this case.

I made this showcase for the absolute beginners who want to know the overview of whole data process from extraction to visualization.

Then, let's get through each process in details

## Building up the ETL Pipelines
This proecess, we will use the Apache Airflow to build up the ETL pipeline along with the process.
As Apache Airflow is the Mac-Native software, we will show the installation through docker so this way it makes the Airflow OS-independent.
### How to set up the Apache Airflow
1. Use the WSL terminal to download the .yaml file using the following command:\
```curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.4/docker-compose.yaml'```
2. Create the following folder to match the setttings in .yaml file.\
```mkdir -p ./dags ./logs ./plugins ./config```
3. Set the permission of current user to virtual environment via\
```echo -e "AIRFLOW_UID=$(id -u)" > .env```
4. Go to ./dags then create DAG via ```dags.py```