FROM local/cent7-latest

# File Author / Maintainer
MAINTAINER fuselabs

# Update yum to get python3.6 repo
RUN  yum -y install https://centos7.iuscommunity.org/ius-release.rpm; yum clean all; yum update -y
# Install python3.6 (and associated pip)
RUN yum -y install python36u python36u-devel; yum -y install python36u-pip
# Install dependencies
RUN pip3.6 install --upgrade pip; pip3.6 install botframework-connector;
RUN yum install libunwind lttng-ust libcurl openssl-libs libuuid krb5-libs libicu zlib gcc gcc-c++ sudo yum install  -y

RUN pip3.6 install spacy
RUN pip3.6 install botbuilder-core
RUN python3.6 -m spacy download en
  
RUN curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
 RUN sh ~/.nvm/nvm.sh && \. ~/.nvm/nvm.sh
RUN sh ~/.nvm/bash_completion && \. ~/.nvm/bash_completion
RUN ls ~/.nvm

# RUN sh ~/.nvm/bash_completion install
RUN sh ~/.nvm/nvm.sh install 8.11.1 
RUN sh ~/.nvm/nvm.sh use 8.11.1 
RUN ls ~/.nvm
RUN yum install epel-release -y
RUN yum install nodejs -y

# Copy sample application
ADD ./PythonBot /PythonBot
ADD ./StateService /StateService

# Get pip to download and install requirements:
RUN npm install StateService
RUN nohup sh node index.js &



EXPOSE 9000
CMD /PythonBot/start.sh
# ENTRYPOINT ["python3.6", "/PythonBot/Bot.py"]
