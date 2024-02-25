#FROM python:3.9-slim
#
#LABEL authors="dj"
#
#WORKDIR /app
#
#COPY . /app
#
#COPY ./requirements.txt /app
#
#RUN pip install --no-cache-dir -r requirements.txt
#
#ENV DISPLAY=:99
#
## Copy SQLite database file to a directory inside the container
#COPY job_db.repository /app/db/
#
## Copy database configuration file to the container
#COPY db.py /app/
#
#CMD ["python", "main.py"]
#
##ENTRYPOINT ["top", "-b"]

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Second <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Use an official Python runtime as a parent image for the build stage
#FROM python:3.9-slim AS build
#
## Set the working directory to /app
#WORKDIR /app
#
## Copy the requirements file
#COPY requirements.txt .
#COPY . /app
## Copy the 'scraping' module
#COPY ./scraping /app/scraping
#COPY ./Config /app/Config
## Install any needed packages specified in requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt
#
## Install Chrome and ChromeDriver
#RUN apt-get update && \apt-get install -y \
#        wget \
#        unzip \
#        gnupg && \
#    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
#    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
#    apt-get update && \
#    apt-get install -y \
#        google-chrome-stable && \
#    CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
#    wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
#    unzip /tmp/chromedriver.zip -d /usr/local/bin && \
#    rm /tmp/chromedriver.zip && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/* \
#
## Create an empty file (to avoid issues if job_db.repository doesn't exist)
#RUN touch job_db.repository
#
## Use a separate image for the final stage
#FROM python:3.9-slim
#
## Set the working directory to /app
#WORKDIR /app
#
## Copy only the necessary files from the build stage
#COPY --from=build /app/requirements.txt /app/
#COPY --from=build /app/.venv /app/.venv
#COPY --from=build /app/job_db.repository /app/db/
#COPY --from=build /app/db.py /app/
#COPY --from=build /app/main.py /app/
#COPY --from=build /app/scraping /app/scraping
#COPY --from=build /app/Config /app/Config
#
#RUN pip install --no-cache-dir -r requirements.txt
#
## Run your script when the container launches
#CMD ["python", "main.py"]


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>THIRD <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
## Use an official Python runtime as a parent image for the build stage
#FROM python:3.9-slim AS build
#
## Set the working directory to /app
#WORKDIR /app
#
## Copy the requirements file and the entire project
#COPY requirements.txt .
#COPY . /app
#
## Copy the 'scraping' module and 'Config' module
#COPY ./scraping /app/scraping
#COPY ./Config /app/Config
#
## Install any needed packages specified in requirements.txt
#RUN apt-get update && \
#    apt-get install -y \
#        wget \
#        curl \
#        unzip \
#        gnupg && \
#    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
#    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
#    apt-get update && \
#    apt-get install -y \
#        google-chrome-stable && \
#    CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
#    wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
#    unzip /tmp/chromedriver.zip -d /usr/local/bin && \
#    rm /tmp/chromedriver.zip && \
#    apt-get clean && \
#    rm -rf /var/lib/apt/lists/* && \
#    pip install --no-cache-dir -r requirements.txt
## Create an empty file (to avoid issues if job_db.repository doesn't exist)
#RUN touch job_db.repository
#
## Use a separate image for the final stage
#FROM python:3.9-slim
#
## Set the working directory to /app
#WORKDIR /app
#
## Copy only the necessary files from the build stage
#COPY --from=build /app/requirements.txt /app/
#COPY --from=build /app/.venv /app/.venv
#COPY --from=build /app/job_db.repository /app/db/
#COPY --from=build /app/db.py /app/
#COPY --from=build /app/main.py /app/
#COPY --from=build /app/scraping /app/scraping
#COPY --from=build /app/Config /app/Config
#COPY --from=build /usr/local/bin/chromedriver /usr/local/bin/chromedriver
#
## Install the required packages
#RUN pip install --no-cache-dir -r requirements.txt
#
## Run your script when the container launches
#CMD ["python", "main.py"]

#>>>>>>>>>>>>>>>>>>>>>>>>>>>> FOURTH <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# Use an official Python runtime as a parent image
FROM python:3.9-slim AS build

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file and the entire project
COPY requirements.txt .
COPY . /app

# Copy the 'scraping' module and 'Config' module
COPY ./scraping /app/scraping
COPY ./Config /app/Config

# Install any needed packages specified in requirements.txt
RUN apt-get update && \
    apt-get install -y \
        wget \
        curl \
        unzip \
        gnupg && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y \
        google-chrome-stable && \
    CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget -q -O /usr/local/bin/chromedriver https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

# Create an empty file (to avoid issues if job_db.repository doesn't exist)
RUN touch job_db.repository

# Use a separate image for the final stage
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=build /app/requirements.txt /app/
COPY --from=build /app/.venv /app/.venv
COPY --from=build /app/job_db.repository /app/db/
COPY --from=build /app/db.py /app/
COPY --from=build /app/main.py /app/
COPY --from=build /app/scraping /app/scraping
COPY --from=build /app/Config /app/Config

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Run your script when the container launches
CMD ["python", "main.py"]
