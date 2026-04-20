from pathlib import Path

from helpers import WIN, skip_if_windows
from pipx.commands.common import _get_list_output, get_exposed_paths_for_package
from pipx.pipx_metadata_file import PackageInfo


def _exe_if_win(apps):
    return [f"{app}.exe" if WIN else app for app in apps]


@skip_if_windows
def test_get_exposed_paths_ignores_recursive_symlink(tmp_path):
    venv_resource_path = tmp_path / "venv_bin"
    venv_resource_path.mkdir()
    local_resource_dir = tmp_path / "bin"
    local_resource_dir.mkdir()
    loop = local_resource_dir / "recursiveexample"
    loop.symlink_to(loop.name)

    exposed = get_exposed_paths_for_package(venv_resource_path, local_resource_dir)

    assert loop not in exposed


def test_get_list_output_with_injected_packages():
    """Test that _get_list_output correctly displays injected packages and their apps."""

    black_apps = _exe_if_win(["black", "blackd"])

    injected_packages_info = {
        "black": {
            "metadata": PackageInfo(
                package="black",
                package_or_url="black==22.8.0",
                pip_args=[],
                include_dependencies=False,
                include_apps=True,
                apps=black_apps,
                app_paths=[],
                apps_of_dependencies=[],
                app_paths_of_dependencies={},
                package_version="22.8.0",
                man_pages=[],
                man_paths=[],
                man_pages_of_dependencies=[],
                man_paths_of_dependencies={},
                suffix="",
                pinned=False,
            ),
            "exposed_binary_names": black_apps,
            "unavailable_binary_names": [],
            "exposed_man_pages": [],
            "unavailable_man_pages": [],
        }
    }

    output = _get_list_output(
        python_version="Python 3.11.0",
        python_is_standalone=False,
        package_version="0.0.0.2",
        package_name="pycowsay",
        new_install=False,
        exposed_binary_names=_exe_if_win(["pycowsay"]),
        unavailable_binary_names=[],
        exposed_man_pages=[str(Path("man6") / "pycowsay.6")],
        unavailable_man_pages=[],
        injected_packages_info=injected_packages_info,
        suffix="",
    )

    assert "Injected Packages:" in output
    assert "black" in output
    assert "22.8.0" in output
    for app in black_apps:
        assert app in output


def test_get_list_output_without_injected_packages():
    """Test that _get_list_output works without injected packages."""

    output = _get_list_output(
        python_version="Python 3.11.0",
        python_is_standalone=False,
        package_version="0.0.0.2",
        package_name="pycowsay",
        new_install=False,
        exposed_binary_names=_exe_if_win(["pycowsay"]),
        unavailable_binary_names=[],
        exposed_man_pages=[str(Path("man6") / "pycowsay.6")],
        unavailable_man_pages=[],
        injected_packages_info=None,
        suffix="",
    )

    assert "Injected Packages:" not in output
    assert "pycowsay" in output
