FROM jupyter/minimal-notebook

MAINTAINER Jiaming Hu <huj22@uw.edu>

USER root

# R pre-requisites
RUN apt-get update && \
    apt-get install -y --no-install-recommends apt-utils \
    fonts-dejavu \
    gfortran \
    gcc 

# Building essentials
RUN apt-get install -y build-essential xorg-dev gcc-multilib gobjc++ libblas-dev libcairo2-dev liblzma-dev gobjc++ libreadline-dev aptitude \
    libbz2-dev libpcre3-dev libcurl4-openssl-dev libssl-dev

# Tools to manage repositories
RUN apt-get install -y software-properties-common \
    wget texinfo texlive texlive-fonts-extra 

# Prepare R environment
ENV RENV_DIR /opt/r-base
ENV RHOME_DIR /home/$NB_USER/rhome
RUN mkdir -p $RENV_DIR && \
    chown $NB_USER $RENV_DIR

ENV PATH $RHOME_DIR/bin:$PATH

USER $NB_USER

RUN mkdir -p $RHOME_DIR

#To get R's blas and lapack must compile from source NOT from deb
RUN cd /tmp && wget https://cran.r-project.org/src/base/R-latest.tar.gz && \
    tar -xzvf R-latest.tar.gz && \
    cd /tmp/R-* && ./configure --prefix=$RENV_DIR --with-cairo && \
    cd /tmp/R-* && make -j 8 && \
    cd /tmp/R-* && make install rhome=$RHOME_DIR

RUN echo "options(bitmapType='cairo')" > /home/$NB_USER/.Rprofile
#need to install in xxx for libraries to be in the right place

RUN Rscript -e "install.packages(c('Cairo', 'RCurl', 'repr', 'IRdisplay', 'evaluate', 'crayon', 'pbdZMQ', 'devtools', 'uuid', 'digest'), repos='http://cran.r-project.org');devtools::install_github('IRkernel/IRkernel');IRkernel::installspec()"

#install components of bioconductor for networkBMA
RUN Rscript -e "source('https://bioconductor.org/biocLite.R');biocLite(c('BMA','Rcpp','RcppArmadillo','RcppEigen','BH','leaps'),ask=FALSE)"

WORKDIR /home/$NB_USER/work