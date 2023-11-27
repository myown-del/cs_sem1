import pathlib
import typing as tp


def update_ref(gitdir: pathlib.Path, ref: tp.Union[str, pathlib.Path], new_value: str) -> None:
    file = gitdir / ref
    file.write_text(new_value)


def symbolic_ref(gitdir: pathlib.Path, name: str, ref: str) -> None:
    if ref_resolve(
            gitdir=gitdir,
            refname=ref
    ):
        file = gitdir / name
        file.write_text(f"ref: {ref}")


def ref_resolve(gitdir: pathlib.Path, refname: str) -> tp.Optional[str]:
    if refname == "HEAD":
        refname = get_ref(gitdir)

    ref_file = gitdir / refname
    if not ref_file.exists():
        return

    return ref_file.read_text()


def resolve_head(gitdir: pathlib.Path) -> tp.Optional[str]:
    return ref_resolve(
        gitdir=gitdir,
        refname="HEAD"
    )


def is_detached(gitdir: pathlib.Path) -> bool:
    file = gitdir / "HEAD"
    file_content = file.read_text()
    return "ref" not in file_content


def get_ref(gitdir: pathlib.Path) -> str:
    file = gitdir / "HEAD"
    return file.read_text().split()[1]
