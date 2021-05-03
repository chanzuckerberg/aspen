from pathlib import Path

import setuptools

description = "ASPEN.  Covid Tracking 2.0"

# NOTE: this is not compatible with a sdist installation of aspen.
requirements_file = Path(__file__).parent / "requirements.txt"
with requirements_file.open("r") as fh:
    requirement_lines = [
        line.strip()
        for line in fh.readlines()
        if line.strip()
        and not (
            line.startswith("-i")
            or line.startswith("-e")
            or line.startswith("#")
            or line.startswith("./")
        )
    ]
print(requirement_lines)

setuptools.setup(
    name="aspen",
    version="0.0.0",
    author=", ".join(
        [
            "Shannon Axelrod",
            "Phoenix Logan",
            "Lucia Reynoso",
            "Tony Tung",
        ]
    ),
    author_email=", ".join(
        [
            "shannon.axelrod@chanzuckerberg.com",
            "phoenix.logan@czbiohub.org",
            "lreynoso@chanzuckerberg.com",
            "ttung@chanzuckerberg.com",
        ]
    ),
    description=description,
    long_description=description,
    packages=setuptools.find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "aspen-cli = aspen.cli.toplevel:cli",
        ]
    },
    include_package_data=True,
    install_requires=requirement_lines,
)
