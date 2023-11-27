import hashlib
import os
import pathlib
import re
import stat
import typing as tp
import zlib

from pyvcs.refs import update_ref
from pyvcs.repo import repo_find


def hash_object(data: bytes, fmt: str, write: bool = False) -> str:
    header = f"{fmt} {len(data)}\0"
    store = header.encode() + data
    hash_ = hashlib.sha1(store).hexdigest()

    if write:
        compressed = zlib.compress(store)

        repo_path = repo_find()
        obj_dir = repo_path / 'objects' / hash_[:2]
        obj_dir.mkdir(parents=True, exist_ok=True)

        obj_path = obj_dir / hash_[2:]
        if not obj_path.exists():
            obj_path.write_bytes(compressed)

    return hash_


def resolve_object(obj_name: str, gitdir: pathlib.Path) -> tp.List[str]:
    if not (4 <= len(obj_name) <= 40):
        raise Exception(f"Not a valid object name {obj_name}")

    obj_dir_name = obj_name[:2]
    obj_file_name = obj_name[2:]
    obj_dir_path = gitdir / "objects" / obj_dir_name

    if not obj_dir_path.is_dir():
        return []

    objs = []
    for item in obj_dir_path.iterdir():
        if item.name.startswith(obj_file_name):
            objs.append(obj_dir_name + item.name)

    if not objs:
        raise Exception(f"Not a valid object name {obj_name}")

    return objs


def find_object(obj_name: str, gitdir: pathlib.Path) -> pathlib.Path:
    return gitdir / "objects" / obj_name[:2] / obj_name[2:]


def read_object(sha: str, gitdir: pathlib.Path) -> tp.Tuple[str, bytes]:
    object_path = find_object(sha, gitdir)

    compressed_data = object_path.read_bytes()
    decompressed_data = zlib.decompress(compressed_data)

    null_byte_index = decompressed_data.index(b'\x00')
    obj_format = decompressed_data[:null_byte_index].decode("utf-8").split(" ")[0]
    obj_content = decompressed_data[null_byte_index + 1:]

    return obj_format, obj_content


def read_tree(data: bytes) -> tp.List[tp.Dict[str, tp.Any]]:
    out = []

    while data:
        mode, data = data.split(b" ", 1)
        mode = int(mode.decode("utf-8"))

        name, data = data.split(b"\x00", 1)
        name = name.decode("utf-8")

        hashed = data[:20].hex()
        data = data[20:]

        out.append({
            "mode": mode,
            "name": name,
            "hash": hashed
        })

    return out


def cat_file(obj_name: str, pretty: bool = True) -> None:
    gitdir = repo_find()
    objs = resolve_object(obj_name, gitdir)
    for obj in objs:
        fmt, data = read_object(obj, gitdir)
        if fmt == "tree":
            result = ""
            tree_files = read_tree(data)
            for file in tree_files:
                result += f"{str(file['mode']).zfill(6)} {read_object(file['hash'], repo_find())[0]} {file['hash']}"
                result += "\t" + file["name"] + "\n"
            print(result)
        else:
            print(str(data, "utf-8"))


def find_tree_files(tree_sha: str, gitdir: pathlib.Path) -> tp.List[tp.Tuple[str, str]]:
    out = []
    fmt, data = read_object(tree_sha, gitdir)

    for file in read_tree(data):
        obj_format, obj_data = read_object(file["hash"], gitdir)

        if obj_format == "tree":
            subtree = find_tree_files(file["hash"], gitdir)
            out.extend([(f"{file['name']}/{f[0]}", f[1]) for f in subtree])
        else:
            out.append((file["name"], file["hash"]))

    return out


def commit_parse(raw: bytes, start: int = 0, dct=None):
    data = zlib.decompress(raw)
    index = data.find(b"tree", start)
    return data[index + 5:index + 45]
