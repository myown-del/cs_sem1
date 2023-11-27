import os
import pathlib
import typing as tp


def get_git_directory_name() -> str:
    return os.environ.get('GIT_DIR', '.git')


def repo_find(workdir: tp.Union[str, pathlib.Path] = ".") -> pathlib.Path:
    workdir = pathlib.Path(workdir)

    while True:
        if (workdir / '.git').is_dir():
            return workdir / '.git'
        else:
            if workdir.parent == pathlib.Path('.'):
                raise ValueError("Not a git repository")
            workdir = workdir.parent


def repo_create(workdir: tp.Union[str, pathlib.Path]) -> pathlib.Path:
    workdir = pathlib.Path(workdir)
    if workdir.is_file():
        raise ValueError(f"{workdir} is not a directory")

    git_dir_name = get_git_directory_name()
    git_dir = workdir / git_dir_name
    git_dir.mkdir(parents=True)

    (git_dir / 'objects').mkdir()
    (git_dir / 'refs' / 'heads').mkdir(parents=True)
    (git_dir / 'refs' / 'tags').mkdir(parents=True)

    (git_dir / 'HEAD').write_text('ref: refs/heads/master\n')

    config_text = '\n\t'.join([
        '[core]',
        'repositoryformatversion = 0',
        'filemode = true',
        'bare = false',
        'logallrefupdates = false\n'
    ])
    (git_dir / 'config').write_text(config_text)

    (git_dir / 'description').write_text('Unnamed pyvcs repository.\n')

    return git_dir
