# Running

```
$ covidmux build-data --start 2022-01-01
Date,P,T,Mean,Ratio
2022-01-01,31.1,194.9,31065,15.9
2022-01-02,66.2,373.7,48652,17.7
2022-01-03,426.1,1917.7,174454,22.2
2022-01-04,335.0,1668.5,214597,20.1
2022-01-05,300.5,1700.5,231781,17.7
2022-01-06,281.2,1892.8,240009,14.9

$ covidmux build-website --dest test
(venv) [clemux@DESKTOP-4QV36P3 covid]$ ls test/
index.html  static
```

# Container

```
podman build -t covid-mux -f container/Dockerfile .
podman run --rm covid-mux -h
docker run --rm -v /var/www/html/covidmux/:/data localhost/covid-mux:latest\
 build-website --dest /data/covid --start 2021-12-01
```

