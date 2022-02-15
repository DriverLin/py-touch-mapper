sudo rclone sync  --http-url http://192.168.1.128:1234 :http:  ./ -P --transfers=64 --exclude .git/
chmod 777 ./jc_debug_run.sh
echo "running command ["`cat ./jc_debug_run.sh`"]" 
./jc_debug_run.sh