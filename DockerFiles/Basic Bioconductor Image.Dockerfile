#xenial image
FROM ubuntu:16.04

#tools to manage repositories
RUN apt-get update && apt-get install -y software-properties-common wget texinfo texlive texlive-fonts-extra

#To get R's blas and lapack must compile from source NOT from deb
RUN wget https://cran.r-project.org/src/base/R-latest.tar.gz
RUN tar -xzvf R-latest.tar.gz

#install stuff for compilation of R

RUN apt-get install -y build-essential gfortran xorg-dev gcc-multilib gobjc++ libblas-dev liblzma-dev gobjc++ libreadline-dev aptitude \
 libbz2-dev libpcre3-dev libcurl4-openssl-dev

#configure and compile
RUN cd R-* && ./configure
RUN cd R-* && make -j 8
RUN cd R-* && make prefix=/ install

#need to install in xxx for libraries to be in the right place

#install components of bioconductor for networkBMA
RUN Rscript -e "source('https://bioconductor.org/biocLite.R');biocLite(c('stats','utils','BMA','Rcpp','RcppArmadillo','RcppEigen','BH','leaps'),ask=FALSE)"

CMD ["/bin/bash"]
