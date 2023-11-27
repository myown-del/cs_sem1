import hashlib
import os
import pathlib
import struct
import typing as tp

from pyvcs.objects import hash_object


class GitIndexEntry(tp.NamedTuple):
    # @see: https://github.com/git/git/blob/master/Documentation/technical/index-format.txt
    ctime_s: int
    ctime_n: int
    mtime_s: int
    mtime_n: int
    dev: int
    ino: int
    mode: int
    uid: int
    gid: int
    size: int
    sha1: bytes
    flags: int
    name: str

    def pack(self) -> bytes:
        return struct.pack(
            f"!4L6i20sh{len(self.name)}s3x",
            *[
                self.ctime_s,
                self.ctime_n,
                self.mtime_s,
                self.mtime_n,
                self.dev,
                self.ino,
                self.mode,
                self.uid,
                self.gid,
                self.size,
                self.sha1,
                self.flags,
                self.name.encode(),
            ],
        )

    @staticmethod
    def unpack(data: bytes) -> "GitIndexEntry":
        unpacked = list(struct.unpack(f"!4L6i20sh{len(data) - 62}s", data))
        remove_fill = unpacked[len(unpacked) - 1]
        unpacked[len(unpacked) - 1] = remove_fill[: len(remove_fill) - 3].decode()
        return GitIndexEntry(*unpacked)


def read_index(git_directory: pathlib.Path) -> tp.List[GitIndexEntry]:
    index_entries = []
    index_file_path = git_directory / "index"

    try:
        index_data = index_file_path.read_bytes()
        entry_count = int.from_bytes(index_data[8:12], "big")
        content = index_data[12:-20]
        current_position = 0
        filler_bytes = b"\x00\x00\x00"

        for _ in range(entry_count):
            start_offset = current_position + 62
            end_offset = start_offset + content[start_offset:].find(filler_bytes) + 3
            entry = GitIndexEntry.unpack(content[current_position:end_offset])
            index_entries.append(entry)
            current_position = end_offset

    finally:
        return index_entries


def write_index(git_directory: pathlib.Path, index_entries: tp.List[GitIndexEntry]) -> None:
    index_file = git_directory / "index"

    # Добавляем header
    index_data = struct.pack("!4s2i", *[b"DIRC", 2, len(index_entries)])

    # Добавляем entries
    for entry in index_entries:
        entry_data = entry.pack()
        index_data += entry_data

    # Добавляем хеш
    hashed_hex = hashlib.sha1(index_data).hexdigest()
    hashed_bytes = bytes.fromhex(hashed_hex)
    index_data_hash = struct.pack(f"!{len(hashed_bytes)}s", hashed_bytes)
    index_data += index_data_hash

    index_file.write_bytes(index_data)


def ls_files(git_directory: pathlib.Path, details: bool = False) -> None:
    index_entries = read_index(git_directory)

    for entry in index_entries:
        if details:
            mode_octal = oct(entry.mode)[2:]
            print(f"{mode_octal} {entry.sha1.hex()} 0\t{entry.name}")
        else:
            print(entry.name)


def update_index(git_directory: pathlib.Path, paths: tp.List[pathlib.Path], write: bool = True) -> None:
    existing_indexes = read_index(git_directory) if (git_directory / "index").exists() else []

    new_indexes = []
    for path in paths:
        content = path.read_bytes()
        hashed = hash_object(content, fmt="blob", write=True)
        stat = os.stat(path)

        new_entry = GitIndexEntry(
            ctime_s=int(stat.st_ctime),
            ctime_n=int(stat.st_ctime_ns) // 1000000000,
            mtime_s=int(stat.st_mtime),
            mtime_n=int(stat.st_mtime_ns) // 1000000000,
            dev=stat.st_dev,
            ino=stat.st_ino,
            mode=stat.st_mode,
            uid=stat.st_uid,
            gid=stat.st_gid,
            size=stat.st_size,
            sha1=bytes.fromhex(hashed),
            flags=7,
            name=str(path.as_posix()),
        )

        new_indexes.append(new_entry)

    updated_indexes = sorted(existing_indexes + new_indexes, key=lambda index: index.name)

    if write:
        write_index(git_directory, updated_indexes)

