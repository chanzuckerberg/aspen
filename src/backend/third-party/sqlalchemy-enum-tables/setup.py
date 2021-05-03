import setuptools as st


def readme():
    with open("README.rst") as f:
        return f.read()


def reqs():
    with open("requirements.txt") as f:
        return f.read()


st.setup(
    name="sqlalchemy_enum_tables",
    packages=st.find_packages(include="enumtables.*"),
    version="1.1.0",
    description="Making Python enums into SQLAlchemy tables with support for Alembic migrations",
    long_description=readme(),
    long_description_content_type="text/x-rst",
    author="Nathan/Eilisha Shiraini",
    author_email="neshiraini+sqlalchemy@heptacle.fr",
    url="https://git.heptacle.fr/neshiraini/sqlalchemy-enum-tables",
    install_requires=reqs(),
    extras_require={
        "Alembic": [
            "alembic",
        ],
    },
    include_package_data=True,
    keywords="sql sqlalchemy orm enum alembic migrations database relational",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Topic :: Database",
    ],
    license="Apache Software License",
    zip_safe=False,
)
