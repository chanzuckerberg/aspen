## AWS setup

### Staging setup

#### AWS Secrets

Create a secret called `aspen-config` with the following contents:

```json
{
  "AUTH0_DOMAIN": "<MY_DOMAIN_HERE>.auth0.com",
  "AUTH0_CLIENT_ID": "<AUTH0_CLIENT_HERE>",
  "AUTH0_CLIENT_SECRET": "<AUTH0_CLIENT_SECRET_HERE>",
  "DB": {
    "admin_username": "<DB_ADMIN_USERNAME>",
    "admin_password": "<DB_ADMIN_PASSWORD>",
    "rw_username": "<USERNAME_FOR_READ_WRITE_USER>",
    "rw_password": "<PASSWORD_FOR_READ_WRITE_USER>",
    "ro_username": "<USERNAME_FOR_READ_ONLY_USER>",
    "ro_password": "<PASSWORD_FOR_READ_ONLY_USER>"
  }
}
```

#### Terraform setup

1. Install terraform:

```bash
aspen% brew tap hashicorp/tap
aspen% brew install hashicorp/tap/terraform
```

2. Source the `environment` file at the top level of the repo. You may need to set `AWS_PROFILE` or `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` in your environment.
3. Run the deployment flow.

```bash
aspen% source environment
aspen% make deploy-tf-initial
```

This should create the policies necessary to deploy to Elastic Beanstalk and create the database. To ensure that passwords are not stored in the terraform state, accounts are created with default passwords. To reset them to match what is stored in AWS Secrets, run `aspen-cli db set-passwords-from-secret --environment <environment>`, where <environment> is either staging or prod. Once the passwords are changed from the default password, subsequent runs of terraform will require pulling the password from AWS secrets to connect to the database. The makefile rule `deploy-tf` manages that process.

```bash
aspen% make deploy-tf
```

## Deploying the python web services

Because the [AWS Elastic Beanstalk CLI](https://github.com/aws/aws-elastic-beanstalk-cli) depends on libraries that conflict with the libraries required by our development workflow, it is recommended to install the AWS EB CLI tools in a separate virtual environment.

1. Set up a virtual environment and install the EB CLI.

```bash
aspen% python -V
Python 3.7.6
aspen% python3.7 -m venv .venv-ebcli
aspen% .venv-ebcli/bin/pip install awsebcli
```

2. Set up the elastic beanstalk configuration in the top-level directory.

```bash
aspen% .venv-ebcli/bin/eb init --region=us-west-2 --platform python-3.7 aspen
```

3. Pick a reasonable identifier for your target deployment environment, such as aspen-<your-user-name>. Create the environment if you haven't done so before. This will deploy the code as well, so if you are doing this step, skip the next one.

```bash
aspen% .venv-ebcli/bin/eb create aspen-<my_username> --cname aspen-<my_username> --envvars AWS_REGION=us-west-2,FLASK_ENV=staging --instance_profile aspen-elasticbeanstalk-ec2-instance-profile
```

If you want ssh access to the EC2 servers, add a ssh keypair using the EC2 console and add `-k <keyname>` to your `eb create` command.

4. If you have already created an environment in the past, just updating the existing deployment environment.

```bash
aspen% .venv-ebcli/bin/eb deploy aspen-myusername
```

5. Visit your deployment. This should open your deployment environment in your browser.

```bash
aspen% .venv-ebcli/bin/eb open aspen-myusername
```

6. Remember to remove your environment when you are not using it.

```bash
aspen% .venv-ebcli/bin/eb terminate aspen-myusername
```

### Granting access to the database.

Access to the database is only granted if an EC2 instance is within the security group `eb-security-group`. Locate your environment in the [Elastic Beanstalk configuration](https://us-west-2.console.aws.amazon.com/elasticbeanstalk/home) page. Find the configuration page for your environment. Then under the category "Instances", click edit. Under EC2 Security Groups, add `eb-security-group` to your launch configuration and restart your environment.

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
