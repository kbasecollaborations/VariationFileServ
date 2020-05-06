docker container kill $(docker ps -q)
docker-compose build 
docker run -v /Users/priyaranjan/kbasecode/VariationFileServ/test_local/workdir:/kb/module/work   -d -i -t -p 5000:5000   variationfileserv_web:latest 
#rm -rf test_local/workdir/*
#python test.py
#perl t.pl
#du -a test_local/workdir/

