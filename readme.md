# International Tourism Analysis: From Local ETL Pipeline to Cloud Deployment
This project is the simple project built as a showcase of ETL process and pipelines building, then we will use those data to perform an analytical review, then visualize them through common visualization tools. The first one is PowerBI, this one shows the connection with MySQL database. Then we design the dashboard on Streamlit, which gives us the decent amount of control over the dashboard content. We also deploy Meta's Llama 3.1 to summarise the data.

After polishing the whole project locally. We also deploy it onto cloud service. We use Amazon Web Services in our project. As concerned on budget, we deploy only ETL pipeline and Streamlit onto AWS.

## Tech Stack
| Layer           | Tool |
|-----------------|------|
| Orchestration (local) | Apache Airflow |
| Containerization | Docker |
| Visualization | PowerBI |
| Database      | PostgreSQL |
| Orchestration (cloud)   | Amazon MWAA |
| Storage         | Amazon S3 |
| Compute         | Amazon EC2 |
| Dashboard       | Streamlit |
| Dashboard Text Generator  | Llama 3.1 |
| CI/CD           | GitHub Actions |
| Reverse Proxy   | nginx |
| Language        | Python 3.13 |
| Libraries       | `pandas`, `numpy`, `wbgapi`, `plotly`, `boto3`, `streamlit`, `huggingface_hub` |


# Phase 1: Project Development

## 1.1 Building up the ETL Pipelines
This proecess, we will use the Apache Airflow to build up the ETL pipeline along with the process.
As Apache Airflow is the Mac-Native software, we will show the installation through docker so this way it makes the Airflow OS-independent.
### How to set up the Apache Airflow
1. Use the WSL terminal to download the .yaml file using the following command:\
```curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.4/docker-compose.yaml'```
2. Create the following folder to match the setttings in .yaml file.\
```mkdir -p ./dags ./logs ./plugins ./config```
3. Set the permission of current user to virtual environment via\
```echo -e "AIRFLOW_UID=$(id -u)" > .env```

At this point, you're able to build up the Airflow Docker container. However, to make this container runs well with this project, you may need some adjustments which I'll explained it on section 1.3 (Docker build adjustment).

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

## 1.2 Get started with World Bank Group API
There's different ways to get the data from various Open API source around the globe. But in case of gathering the data from World Bank Group, we could use `wbgapi` which is the one of the most common third-party python libraty to connect with World Bank Group open data.

You could get along with very first part of `etl.py / extract_transform_load()` method to understand what's going on behind the scene there.

After downloading and import the library into the script aliased as `wb` we could use `wb.data.DataFrame()` method to fetch the data from the World Bank Group. Then we need to do some transform and cleanup the data as we want before loading into the database. The setting is in accordance with thsoe in `docker-compose.yaml / services / postgres` section, and the table name as specified in `db_load.py`.

## 1.3 Docker build adjustment
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
       

## 1.4 Test the dag with airflow GUI
After container and dag buiding, we will acccess the Airflow GUI to test what we've worked so far. We could access airflow GUI through http://localhost:8080 in your browser of your choice by default. We could see those configuration from `docker-compose.yaml`

## 1.5 Query data from the database
If you follow step 3 correctly, it's supposed that the file was writted into the database the name specified in `dbconfig.py`. We gonna query it from the database, then export into new csv file.

Briefly, the new task follows these steps:
- **Create** engine using connection string predefined in `dbconfig.py`
- **Specify** the SQL query.
- **Use** `read_sql_query()` to connect with the database using predefined query and engine, then export to .csv files
- **Close** the connection to the database.

As we need this tasks to perform automatically, we also need to include this tasks in dag. So, we need to wrap this process into callable function, then add this tasks to dag.

## 1.6 Connect to the database and visualize with powerBI
At this point, we expect that we are able to run the DAG as it supposed to be. Now we gonna import the data from the database, then visulize it. To connect the database with powerBI, we might have to connect to server named `127.0.0.1:5432` as we expose this port from container to global environment and other settings e.g. database name, username, and password as defined in `docker-compose.yaml`

There's the number of skillsets required to build up the visualization, but here's the list of skills used in this file;
- Transform the data
- Dashboard building
- Adding both new and quick measurements

## 1.7 Build AI-Enhanced Dashboard with Streamlit (Sep 4, 2025)
Another form of deliverables is into the web-based so it was able to share with broader scale of end-users. Here we gonna use Streamlit [https://streamlit.io] to build up the lightweight web application using python.
Briefly, we built up the dashboard based on visualization already built from PowerBI as described in section 5.

Moreover, we enhance the narration capability with Llama3.1 AI models using huggingface's API so they're able to give users the AI-generated narrative based on given data.

# Phase 2: Project Deployment (Sep 14, 2025)
After developing end-to-end projects in local machine, in this phase we will deploy the ETL pipeline and Streamlit Dashvoard to public cloud services. In this projet we'll introduce you the following services from AWS:
- **S3**, as AWS's multi-purposed storage services. Basically, their storage unit is called 'bucket'. We will use S3 to store AIrflow's DAG and ETL output.
- **Managed Workflow for Apache Airflow (MWAA)** will be used for orchestrate the pipeline using DAG. Deployment in MWAA give us the advantage to keep the pipeline active 24/7.
- **EC2** takes responsiblity as webserver to run and host Streamlit Dashboard onto the internet.

So let's get started.

## 2.1 Create S3 buckets
Firstly, we need to create the new S3 bucket from AWS Management Console > S3. Then create general purpose buckets and block all public access. You could set the rest of configuration as you want, but we'll leave it as it is for our project. Then create the bucket.

## 2.2 Create new IAM users
After creating the new buckets. We will create the new IAM users to control the service access only with S3 services to prevent protent leakage of confidential data.

We go to AWS Console > IAM > Users > Create users to create the new users. After create the new users, go to Permissions > Add Permissions. Then add AmazonS3FullAccess to the users.

Then we go to 'Security Credential' and create the access key. We got `Access key ID` and `Secret access key` which we will use for credential later in phase 2.4

## 2.3 Manually Add file to S3 buckets
After creating S3 buckets, we will manually add the file to S3 bucket into the file and folder. Here's the S3 file directory.

```
.
├── dags
│   ├── dags.py
│   ├── etl.py
│   └── metrics.py
├── data                    # we leave /data folder blank as we will put the ETL output here
└── requirements.txt
```

For now, we will deploy the project using .csv files so we will not use SQL-related components in cloud version of dags.

## 2.4 Create CI-CD pipeline via Github Actions
After phase 2.3, you guys might find out that manually adding the files into bucket using UI is a bit overwhelming especially when the dashboard is in development phase. So, here's how to deploy the file automatically form your github repository using Github Actions.

First, you need to create the new workflow as `.yml` file under `.github/workflows` folder. It should look like this
```
.
└── .github/workflows
    └── mwaa-actions.yml
```
Then we build the pipeline as detailed in the file. Basically, with this workflow, the file in S3 bucket will be updated eveytime we push the code onto Github repo. Don't forget to keep the `Access key ID` and `Secret access key` into Github repository via **settings > secrets and variables > actions.**

## 2.5 Build on-cloud ETL pipleline using Amazon MWAA
Then, after we upload the dags components into S3 buckets, we will orchestrate the dag with MWAA. MWAA (Managed Workflow for Apache Airflow) is the Amazon's service to host the Apache Airflow to run on Amazon's cloud environment. It requires dag stored in S3, which we created earlier, and VPC, which we will create here in MWAA environment.

Environment creation is so simple with Management Console UI. You could select airflow version, maintenance windows. S3 bucket, dag folder, and requirements. Of course Amazon provide a range of options to build your new environment as as you need e.g. class, VPCs, security groups, and more.

After you create an environment, you could click on "Open Airflow UI" then go to your dags to see if your ETL pipeline is running properly.

When dags processed properly, it will generated the file `data.csv` located in `data` folder in S3 buckets. This data will be accessed by EC2 for the dashboard.

## 2.6 Launch and access into EC2 instance
As we need to deploy streamlit dashboard to be publicly accessible. We need EC2 compute instance to render the dashboard from python script and host it as a webserver.

We will launch the instance using the OS of your choice (this project we use **Ubuntu** Server, however). We need to config the EC2 instance at least as follows:
- EC2 instance must be associated with the same VPC that MWAA environments created on.
- We will host it on the public subnet for instance accessibility.
- `.pem` file should be created as we might use it as credentials when accessing this instance with Secure Shell (SSH) from local machines. Don't forget to check 'Allow SSH traffic from Anywhere'. Download `.pem` file in your working dierectory.
- We need to attached Security Groups to this EC2 instance for security reasons. Here's inbound rules requirements:
    - Allow SSH type of TCP protocol to your IP. This allows us to access the instance from local machine.
    - Allow Custom TCP protocal from 0.0.0.0/0 port 8501. We expose port 8501 as a Streamlit default port to the internet, so users must access this EC2 instance through port 8501 to see the Streamlit dashboard.

We could leave the other part as it is. We could also execute shell script in 'User Data' upon instance launch, but we will let it as blank here becuase we will use another approach for better maintainability.

Apart from S3 and MWAA, EC2 was made for general purpose computing. So basically, EC2 instance is another computer that you rent from Amazon. We will talk about how to access and use it in the next phase, we will use **EC2 public IP address** and .pem files.

Then, open your terminal either powershell or bash. Move to your working directory with `cd` command, then enter the following command.
``` 
-- local terminal --

cd <path-to-your-working-folder>
ssh -i <your-pem-key>.pem ubuntu@<EC2-public-ip-address>
```

This will take you to the EC2 instance at the home directory (`/home/ubuntu`). You could do anything with it through your terminal.

### 2.7 Upload Dashboard onto EC2 instance
There're ways to upload your file into the EC2 instance. But for now we will simply manually copy the files in our local manchine into EC2 instance with the following command.
```
-- EC2 terminal --

scp -i your-key.pem streamlit_dashboard.py ubuntu@<EC2-public-ip-address>:/home/ubuntu/
```
Then, your streamlit files is already upload onto your EC2 instance.

### 2.8 Install packages, libraries, and virtual environment.
Initially, EC2 is the virtual machine with only OS and limit sets of software to make it works. Here's the thing that you should know about this topic.
- After you stop and start the instance again, you installed packages and libraries will be wiped from the instance. So, we need to build up the worklow to automatically install them right after we boot the instance.
- First, we will create the shell script which contains bash command to install packages and libraries. We will execute them after creation of virtual environment.
- As Ubuntu EC2 instance doesn't accept the instance wide libraries anymore, we need to create virtual environment before proceeding.
- Then we will execute those shell script through Ubuntu's systemd which will be executed after restart the instance.

#### Create a startup script
At working directory, we create new shell script file, in this case we named it `startup.sh` then we put in the set of commands as follows:
```
-- startup.sh --

#!/bin/bash

# install the required libraries/packages
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip git nginx -y

# create virtual environment on working directory, then activate it
python -m venv /home/ubuntu
source /home/ubuntu/bin/activate

# under the virutal environment install the remaining libraries in virtual environment
sudo pip install awscli streamlit plotly pandas numpy scipy huggingface_hub boto3

# copy the data files from S3 bucket
aws s3 cp s3://wb-travel-s3buckets/data/data.csv /home/ubuntu/data/data.csv

# run the streamlit
streamlit run streamlit_dashboard.py
```
Then, we will make this file executable by the system using:
```
-- EC2 Terminal --

sudo chown ubuntu:ubuntu /home/ubuntu/startup.sh
chmod +x /home/ubuntu/startup.sh
```

#### Crete and run systemd file
Then we will create the new service file for system to execute, we will point them at `startup.sh` previously created and put the huggingface token here.

First, create the new file in `system` folder using:
```
-- EC2 terminal --

sudo nano /etc/systemd/system/startup.service
```

Then, enter the following scripts:
```
-- startup.service --
[Unit]
Description=Run Custom shell script at boot
After=network.target

[Service]
ExecStart=/home/ubuntu/startup.sh
User=ubuntu
WorkingDirectory=/home/ubuntu
Environment="HF_TOKEN=<your-hf-token>"
StandardOutput=journal
StandardError=journal
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
```
Then eexecute this systemd file by making daemon reload them then enable and start the systemfile.
```
-- EC2 instance --

sudo systemctl daemon-reload
sudo systemctl enable startup.service
sudo systemctl start startup.service
```
At this point after you stop and restart the EC2 instance, the installed package still persist. You could access to streamlit dashboard using `http://<EC2-public-IP>:8501` in your browser.

### 2.9 Reverse Proxy with Nginx
When we doesn't want to add up your port number everytime you access the page. You could do reverse proxy with nginx as follows:

First, we will create the new nginx config file:
```
-- EC2 terminal --

sudo nano /etc/nginx/sites-available/streamlit
```
Then input the following config in the file
```
-- streamlit (nginx config file) --

server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Then reload nginx:
```
-- EC2 terminal --

sudo ln -s /etc/nginx/sites-available/streamlit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
With this you could access the streamlit using `http://<EC2-public-ip>` without the port number specified.

### 2.10 Fix your public IP with AWS Elastic IP service
Since we create EC2 instance with public access. By default, EC2 public ip will be randomly allocated everytime you start the instance. So, to fix the public IP number, we go to Elastic IPs service, then allocate the elastic IP address to our EC2 instance so this would fix the IP address.

Then we could use this allocated IP to register the domain with Amazon Route 53, which is DNS service offered by Amazon.