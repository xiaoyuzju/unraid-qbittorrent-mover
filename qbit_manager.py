import os
import sys
import json
import shutil
import argparse

from typing import List
from pathlib import Path
from dataclasses import dataclass
from qbittorrentapi import Client, TorrentDictionary


@dataclass
class ContainerVolume:
    container_path: str
    host_path: str


class QbitManager:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        container_volumes: List[ContainerVolume],
    ):
        self.host = host
        self.username = username
        self.password = password
        self.container_volumes = container_volumes
        self.client = Client(
            host=self.host,
            username=self.username,
            password=self.password,
        )
        self.json_path = Path(__file__).parent / "torrent_hash_list.json"

    def is_torrent_in_cache(self, torrent: TorrentDictionary) -> bool:
        torrent_container_path = torrent.content_path
        for volume in self.container_volumes:
            if torrent_container_path.startswith(volume.container_path):
                torrent_host_path = torrent_container_path.replace(
                    volume.container_path,
                    volume.host_path,
                )
                break

        return Path(torrent_host_path).exists()

    def pause_torrents(self):
        torrent_hash_list = list()
        for torrent in self.client.torrents_info():
            if self.is_torrent_in_cache(torrent):
                print(
                    f"Torrent {torrent.name} (hash: {torrent.info.hash}) is in cache, pausing"
                )
                torrent_hash_list.append(torrent.info.hash)

        print(f"Pausing {len(torrent_hash_list)} torrents")
        self.client.torrents_pause(torrent_hash_list)

        with open(self.json_path, "w") as f:
            json.dump(torrent_hash_list, f)

    def resume_torrents(self):
        with open(self.json_path, "r") as f:
            torrent_hash_list = json.load(f)

        print(f"Resuming {len(torrent_hash_list)} torrents")
        self.client.torrents_resume(torrent_hash_list)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        type=str,
        required=True,
        help="qbittorrent host",
    )
    parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="qbittorrent username",
    )
    parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="qbittorrent password",
    )
    parser.add_argument(
        "--container-mapping",
        type=str,
        nargs="+",
        required=True,
        help="container path and host path mapping",
    )
    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        help="pause or resume",
    )
    parser.add_argument(
        "--used-percentage-threshold",
        type=int,
        default=75,
        help="used percentage threshold for cache usage",
    )
    args = parser.parse_args()

    container_mapping_list = args.container_mapping
    qbit = QbitManager(
        host=args.host,
        username=args.username,
        password=args.password,
        container_volumes=[
            ContainerVolume(
                container_path=mapping.split(":")[0],
                host_path=mapping.split(":")[1],
            )
            for mapping in container_mapping_list
        ],
    )
    if args.mode == "pause":
        total, used, free = shutil.disk_usage("/mnt/cache")
        used_percentage = used / total * 100
        print(
            f"Cache usage: {used_percentage:.2f}% "
            f"Total: {total / (1024 * 1024 * 1024):.2f} GB "
            f"Used: {used / (1024 * 1024 * 1024):.2f} GB "
            f"Free: {free / (1024 * 1024 * 1024):.2f} GB"
        )
        qbit.json_path.unlink(missing_ok=True)
        if used_percentage > args.used_percentage_threshold:
            print(f"Cache usage is above {args.used_percentage_threshold}%")
            qbit.pause_torrents()
        else:
            print(f"Cache usage is below {args.used_percentage_threshold}%")
    elif args.mode == "resume":
        if qbit.json_path.exists():
            qbit.resume_torrents()
    else:
        print(f"Invalid mode: {args.mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
