import os
import pathlib
import shutil
import typing as tp

from pyvcs.index import read_index, update_index
from pyvcs.objects import commit_parse, find_object, find_tree_files, read_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref
from pyvcs.tree import commit_tree, write_tree


def add(gitdir: pathlib.Path, paths: tp.List[pathlib.Path]) -> None:
    update_index(
        git_directory=gitdir,
        paths=paths
    )


def commit(gitdir: pathlib.Path, message: str, author: tp.Optional[str] = None) -> str:
    return commit_tree(
        git_directory=gitdir,
        tree=write_tree(
            gitdir=gitdir,
            index=read_index(gitdir)
        ),
        message=message,
        author=author
    )


def checkout(gitdir: pathlib.Path, obj_name: str) -> None:
    head = gitdir / "refs/heads" / obj_name

    if head.exists():
        obj_name = head.read_text()

    index = read_index(gitdir)

    for file_entry in index:
        file_path = pathlib.Path(file_entry.name)

        if file_path.is_file():
            name_parts = file_path.parts
            if len(name_parts) > 1:
                shutil.rmtree(name_parts[0])
            else:
                os.chmod(file_entry.name, 0o777)
                os.remove(file_entry.name)

    path = gitdir / "objects" / obj_name[:2] / obj_name[2:]
    data = path.read_bytes()

    commit_hash = commit_parse(data).decode()

    for file_info in find_tree_files(commit_hash, gitdir):
        name_parts = file_info[0].split("/")

        if len(name_parts) > 1:
            try:
                pathlib.Path(name_parts[0]).absolute().mkdir()
            except OSError:
                pass

        fmt, file_data = read_object(file_info[1], gitdir)

        with open(file_info[0], "w") as file:
            file.write(str(file_data, "utf-8"))

