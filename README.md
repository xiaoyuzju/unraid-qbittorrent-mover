# unraid-qbittorrent-mover

Pause or resume the torrents so that mover can move files

When you make use of the unRAID cache drive for your qBittorrent's download directory, and the torrents in qBittorrent are still seeding, the mover can't move files since they are still in use.

This project provides a python script that can pause and resume torrents if their directories are in the cache, and a user script to automatically modify the mover file to use the python script.



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

4. add new user script `qbit_mover`, and make it run `At Startup of Array` 

   ```bash
   #!/bin/bash
   
   grep -q 'mode pause' /usr/local/sbin/mover || sed -ik -e '/mover: started/{' -e 'a \ \ /mnt/user/appdata/qbit_mover/venv/bin/python /mnt/user/appdata/qbit_mover/qbit_manager.py --mode pause --host http://[IP]:[PORT] --username [user] --password [passwd] --container-mapping [/media:/mnt/cache/media] --used-percentage-threshold [75]' -e '}' /usr/local/sbin/mover
   
   grep -q 'mode resume' /usr/local/sbin/mover || sed -i -e '/mover: started/{' -e 'a \ \ /mnt/user/appdata/qbit_mover/venv/bin/python /mnt/user/appdata/qbit_mover/qbit_manager.py --mode resume --host http://[IP]:[PORT] --username [user] --password [passwd] --container-mapping [/media:/mnt/cache/media] --used-percentage-threshold [75]' -e '}' /usr/local/sbin/mover
   
   ```

   

## ref

https://trash-guides.info/Downloaders/qBittorrent/Tips/How-to-run-the-unRaid-mover-for-qBittorrent/#python-venv

