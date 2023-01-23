from pathlib import Path
from typing import List, Union

import setuptools  # type: ignore

HERE = Path(__file__).parent


def get_requirements(path: Union[str, Path]) -> List[str]:
    with open(HERE / path, encoding="utf8") as file:
        content = file.readlines()
    return content


REQUIRES = get_requirements("requirements.txt")
DEV_REQUIRES = get_requirements("requirements_dev.txt") + REQUIRES


setuptools.setup(
    use_scm_version=True,
    install_requires=REQUIRES,
    tests_require=DEV_REQUIRES,
    extras_require={"dev": DEV_REQUIRES},
    package_dir={"shadow_lib": "shadow_lib"},
    packages=setuptools.find_packages(exclude=["tests", "migrations"]),
)
