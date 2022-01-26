FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN apt update

# insall xvfb

RUN pip install bs4 undetected_chromedriver xvfbwrapper
RUN apt -f install -y

#RUN curl -LO https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
#RUN apt-get install -y ./google-chrome-stable_current_amd64.deb
#RUN rm google-chrome-stable_current_amd64.deb 
