import os
import pathlib
import stat
import time
import typing as tp
from collections import deque

from pyvcs.index import GitIndexEntry, read_index
from pyvcs.objects import hash_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref


def write_tree(gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = "") -> str:
    def create_file_entry(mode: bytes, name: bytes, sha1: bytes) -> bytes:
        return b''.join([
            mode,
            b" ",
            name,
            b"\0",
            sha1
        ])

    tree_content = b""
    stack = deque(index)

    while stack:
        entry = stack.popleft()
        path = entry.name.split("/")

        is_tree = len(path) > 1
        if is_tree:
            header = b"40000 " + path[0].encode() + b"\0"
            tree_content += header

            file_entry = create_file_entry(
                mode=oct(entry.mode)[2:].encode(),
                name="/".join(path[1:]).encode(),
                sha1=entry.sha1
            )

            hashed = hash_object(file_entry, fmt="tree", write=True)
            tree_content += bytes.fromhex(hashed)

            subtree_entries = [e for e in index if e.name.startswith(entry.name + "/")]
            stack.extend(subtree_entries)
        else:
            file_entry = create_file_entry(
                mode=oct(entry.mode)[2:].encode(),
                name=path[0].encode(),
                sha1=entry.sha1
            )
            tree_content += file_entry

    return hash_object(tree_content, fmt="tree", write=True)


def commit_tree(
        git_directory: pathlib.Path,
        tree: str,
        message: str,
        parent: tp.Optional[str] = None,
        author: tp.Optional[str] = None,
) -> str:
    timestamp = int(time.mktime(time.localtime()))
    tz_sign = "+" if time.timezone < 0 else "-"

    tz_hours = abs(time.timezone // 3600)
    tz_hours_str = f"0{tz_hours}" if tz_hours < 10 else str(tz_hours)

    tz_secs = abs((time.timezone // 60) % 60)
    tz_secs_str = f"0{tz_secs}" if tz_secs < 10 else str(tz_secs)

    content_time = f"{timestamp} {tz_sign}{tz_hours_str}{tz_secs_str}"
    content = f"tree {tree}\n"

    if parent:
        content += f"parent {parent}\n"

    content += '\n'.join([
        f"author {author} {content_time}",
        f"committer {author} {content_time}",
        f"",
        f"{message}",
        f""
    ])
    hashed = hash_object(
        data=content.encode("ascii"),
        fmt="commit",
        write=True
    )

    return hashed

