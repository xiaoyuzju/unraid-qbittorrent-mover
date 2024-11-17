# unraid-qbittorrent-mover

Pause or resume the torrents so that mover can move files



## usage

1. install application `python3 for unraid` 

2. create venv

   ```bash
   mkdir -p /mnt/user/appdata/qbit_mover/venv
   source /mnt/user/appdata/qbit_mover/venv/bin/activate
   pip install qbittorrent-api
   deactivate
   ```

3. download `qbit_manager.py` to `/mnt/user/appdata/qbit_mover/qbit_manager.py`

4. add new user script `qbit_mover`

   ```bash
   #!/bin/bash
   
   grep -q 'mode pause' /usr/local/sbin/mover || sed -ik -e '/mover: started/{' -e 'a \ \ /mnt/user/appdata/qbit_mover/venv/bin/python /mnt/user/appdata/qbit_mover/qbit_manager.py --mode pause --host http://[IP]:[PORT] --username [user] --password [passwd] --container-mapping [/media:/mnt/cache/media] --used-percentage-threshold 75' -e '}' /usr/local/sbin/mover
   
   grep -q 'mode resume' /usr/local/sbin/mover || sed -ik -e '/mover: started/{' -e 'a \ \ /mnt/user/appdata/qbit_mover/venv/bin/python /mnt/user/appdata/qbit_mover/qbit_manager.py --mode resume --host http://[IP]:[PORT] --username [user] --password [passwd] --container-mapping [/media:/mnt/cache/media] --used-percentage-threshold 75' -e '}' /usr/local/sbin/mover
   
   ```

   

