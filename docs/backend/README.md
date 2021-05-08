## Database concerns

### Interacting with the local database in sql

You can also connect to your local psql console by running:

```
aspen% make local-pgconsole
psql (13.1)
Type "help" for help.

aspen_db=> select * from aspen.users;
 id | name | email | auth0_user_id | group_admin | system_admin | group_id
----+------+-------+---------------+-------------+--------------+----------
(0 rows)

aspen_db=>
```

### Interacting with the local database in python

It is possible to interact with the local database in ipython:

```
aspen% make local-dbconsole
docker-compose exec utility aspen-cli db --docker interact
Python 3.9.1 (default, Feb  9 2021, 07:55:26)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.21.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: session = engine.make_session()

In [2]: session.query(User).all()
Out[2]: []

In [3]:
```

### Profiling SqlAlchemy queries

#### Interactive profiling

`aspen-cli db interact` has a `--profile` option that prints out every query that's executed and how long they take:

```
aspen% make local-dbconsole-profile
docker-compose exec utility aspen-cli db --docker interact --profile
Python 3.9.1 (default, Feb  9 2021, 07:55:26)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.21.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: session = engine.make_session()

In [2]: results = session.query(Sample).all()
DEBUG:sqltime:Start Query: SELECT aspen.samples.id AS aspen_samples_id, aspen.samples.submitting_group_id AS aspen_samples_submitting_group_id, aspen.samples.private_identifier AS aspen_samples_private_identifier, aspen.samples.original_submission AS aspen_samples_original_submission, aspen.samples.public_identifier AS aspen_samples_public_identifier, aspen.samples.sample_collected_by AS aspen_samples_sample_collected_by, aspen.samples.sample_collector_contact_email AS aspen_samples_sample_collector_contact_email, aspen.samples.sample_collector_contact_address AS aspen_samples_sample_collector_contact_address, aspen.samples.authors AS aspen_samples_authors, aspen.samples.collection_date AS aspen_samples_collection_date, aspen.samples.location AS aspen_samples_location, aspen.samples.division AS aspen_samples_division, aspen.samples.country AS aspen_samples_country, aspen.samples.organism AS aspen_samples_organism, aspen.samples.host AS aspen_samples_host, aspen.samples.purpose_of_sampling AS aspen_samples_purpose_of_sampling, aspen.samples.specimen_processing AS aspen_samples_specimen_processing
FROM aspen.samples
DEBUG:sqltime:Query Complete!
DEBUG:sqltime:Total Time: 0.012416

In [3]:
```

#### Profiling in code

The module [`aspen.database.connection`](../../src/backend/aspen/database/connection.py) contains a number of methods to manage the capture of queries issued by sqlalchemy.  `enable_profiling()`/`disable_profiling()` can be used to enable and disable profiling, and `enable_profiling_ctx()` is a [context manager](https://docs.python.org/3/reference/compound_stmts.html#with) that can be used to manage a block of code that requires profiling.

### Autogeneration of schema migration

- after modifying/adding any database table/schema code run:
  - `make utility-alembic-autogenerate MESSAGE="descriptive message"`
- this will create a migration file under `src/backend/database_migrations`
  - make sure you look this file over and verify that alembic made the appropriate changes
- run `make utility-alembic-upgrade-head`
  - this updates your local running database, make sure you use either `make pg-console` or `make db-console` to check that changes were applied appropriately!

## Updating python dependencies

To update python dependencies, update the [`Pipfile`](../../Pipfile) and run `make update-deps`. This will update [`Pipfile.lock`](../../src/backend/Pipfile.lock) and [`requirements.txt`](../../src/backend/requirements.txt) (used by setup.py).
You will also need to rebuild local running docker containers by running `make local-rebuild`.

If you add a third-party library (directly or indirectly) that does not support [python typing](https://docs.python.org/3/library/typing.html), then you may need to add an entry to [`mypy.ini`](../../mypy.ini) to let mypy know [not to expect type hints for that library](https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-type-hints-for-third-party-library).


## Adding new users to the staging db:
* get username / password credentials from aws secrets manager (:
  * `aws secretsmanager get-secret-value --secret-id aspen-config`

* get RDS host and port information:
  * `aws rds describe-db-instances --db-instance-identifier aspen-db`

* connect to aspen db using psql:
  * `psql -h <RDS host> -p <RDS port> -U user_rw aspen_db`
    ```sql
    aspen_db=> set search_path to aspen;
    aspen_db=> INSERT INTO users (name, email, auth0_user_id, group_admin, system_admin, group_id) VALUES ('<name>', '<email>', '<auth0 user ID>', 'f', 't', <group ID>);
    ```
    * to see all possible group ids:
      * `select * from groups;`
