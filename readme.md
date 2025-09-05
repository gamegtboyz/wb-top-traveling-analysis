# Historical Trends of Tourism Analysis
This project is the simple project built as a showcase of ETL process and pipelines building, then we will use those data to perform an analytical review, then visualize them through common BI tools -- We gonna use PowerBI in this case.

I made this showcase for the absolute beginners who want to know the overview of whole data process from extraction to visualization.

Then, let's get through each process in details

## 1. Building up the ETL Pipelines
This proecess, we will use the Apache Airflow to build up the ETL pipeline along with the process.
As Apache Airflow is the Mac-Native software, we will show the installation through docker so this way it makes the Airflow OS-independent.
### How to set up the Apache Airflow
1. Use the WSL terminal to download the .yaml file using the following command:\
```curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.4/docker-compose.yaml'```
2. Create the following folder to match the setttings in .yaml file.\
```mkdir -p ./dags ./logs ./plugins ./config```
3. Set the permission of current user to virtual environment via\
```echo -e "AIRFLOW_UID=$(id -u)" > .env```

At this point, you're able to build up the Airflow Docker container. However, to make this container runs well with this project, you may need some adjustments which I'll explained it on section 3. (Docker build adjustment).

### Create DAG (Directed Acyclic Graph)
When you already built the airflow docker container. It's implied that we've already install airflow into our project. Then, we will create the DAG (Directed Acyclic Graph), which is basically the python script used to tell the airflow when and what tasks they need to run.

First, you need to create the file called `dags.py` in `./dags` folder, import at least the following
```
--dags.py--

from datetime import datetime, timedelta    # we will use it to config the schedule and execution interval
from airflow.models.dag import DAG          # import the DAG object
```
Then import the operators e.g. `PythonOperator`,`BashOperator`, and tasks which must be in the form of callable function.

Then we will create the tasks in python script and wrap it into callable function. In this case we use `etl.py` and `db_load.py` as a task. We could see the details from file as mentioned.

Then we need to specify the tasks dependencies as detailed in the very bottom part of `dags.py`.

## 2. Get started with World Bank Group API
There's different ways to get the data from various Open API source around the globe. But in case of gathering the data from World Bank Group, we could use `wbgapi` which is the one of the most common third-party python libraty to connect with World Bank Group open data.

You could get along with very first part of `etl.py / extract_transform_load()` method to understand what's going on behind the scene there.

After downloading and import the library into the script aliased as `wb` we could use `wb.data.DataFrame()` method to fetch the data from the World Bank Group. Then we need to do some transform and cleanup the data as we want before loading into the database. The setting is in accordance with thsoe in `docker-compose.yaml / services / postgres` section, and the table name as specified in `db_load.py`.

## 3. Docker build adjustment
When you proceed from this point, you might face some errors due to the docker build. Here we will inspect for an errors which I found, and how to fix it.
### Install the library or upgrade airflow version
As some libraries may not be initially installed in the docker image, you may need to install them manually by adjusting the docker image:
- Create a `Dockerfile` in the same directory as `docker-compose.yaml`. Install the required Airflow version or additional libraries in the `Dockerfile`.
- In `docker-compose.yaml`, go to the `x-airflow-common/build` section (around line 52) and uncomment it to enable custom package installation.

### File output location
If you cannot find the output `.csv` file after executing Airflow, it may have been generated inside the container. To ensure the output file is located in your working folder:
- Open `docker-compose.yaml` and go to the `x-airflow-common / volumes` section (around row 75).
- Check the configuration for the folders corresponding to those you created.
- Add a new line to map the output directory. For example, to use a folder named `data`, add the new folder so it look like this:

       --docker-compose.yaml--

       x-airflow-common:
        volumes:
            - ${AIRFLOW_PROJ_DIR:-.}/dags:/opt/airflow/dags
            - ${AIRFLOW_PROJ_DIR:-.}/logs:/opt/airflow/logs
            - ${AIRFLOW_PROJ_DIR:-.}/config:/opt/airflow/config
            - ${AIRFLOW_PROJ_DIR:-.}/plugins:/opt/airflow/plugins
            - ${AIRFLOW_PROJ_DIR:-.}/data:/opt/airflow/data
       
- Create a new folder named `data` in your project directory to store the output files.

### Expose postgreSQL's port 5432 to localhost
We also need to expose the postgreSQL in container's instance to global environment. We have to adjust the `service / postgres` section by adding the `ports` parameter like this:

    --docker-compose.yaml--
    
    services:
        postgres:
            ports:
                - "5432:5432"

This exposure will be useful when we connect the database to powerBI for visualization.

### Rebuild Docker Container
After adjust all items above, we need to rebuild the docker container to register the changes to the container. We could do that using the following command:

    --Bash--

    docker-compose build
    docker-compose up -d
       

## 4. Test the dag with airflow GUI
After container and dag buiding, we will acccess the Airflow GUI to test what we've worked so far. We could access airflow GUI through http://localhost:8080 in your browser of your choice by default. We could see those configuration from `docker-compose.yaml`

## 5. Connect to the database and visualize with powerBI
At this point, we expect that we are able to run the DAG as it supposed to be. Now we gonna import the data from the database, then visulize it. To connect the database with powerBI, we might have to connect to server named `127.0.0.1:5432` as we expose this port from container to global environment and other settings e.g. database name, username, and password as defined in `docker-compose.yaml`

There's the number of skillsets required to build up the visualization, but here's the list of skills used in this file;
- Transform the data
- Dashboard building
- Adding both new and quick measurements

## 6. Query data from the database
If you follow step 3 correctly, it's supposed that the file was writted into the database the name specified in `dbconfig.py`. We gonna query it from the database, then export into new csv file.

Briefly, the new task follows these steps:
- **Create** engine using connection string predefined in `dbconfig.py`
- **Specify** the SQL query.
- **Use** `read_sql_query()` to connect with the database using predefined query and engine, then export to .csv files
- **Close** the connection to the database.

As we need this tasks to perform automatically, we also need to include this tasks in dag. So, we need to wrap this process into callable function, then add this tasks to dag.

## 7. Build AI-Enhanced Dashboard with Streamlit (Sep 4, 2025)
Another form of deliverables is into the web-based so it was able to share with broader scale of end-users. Here we gonna use Streamlit [https://streamlit.io] to build up the lightweight web application using python.
Briefly, we built up the dashboard based on visualization already built from PowerBI as described in section 5.

Moreover, we enhance the narration capability with Llama3.1 AI models using huggingface's API so they're able to give users the AI-generated narrative based on given data.