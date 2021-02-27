import click
from IPython.terminal.embed import InteractiveShellEmbed

from aspen.cli.toplevel import cli
from aspen.config.development import DevelopmentConfig
from aspen.covidhub_import import import_project
from aspen.database.connection import enable_profiling, get_db_uri, init_db
from aspen.database.models import *  # noqa: F401, F403
from aspen.database.schema import create_tables_and_schema


@cli.group()
@click.pass_context
def db(ctx):
    # TODO: support multiple runtime environments.
    ctx.obj["ENGINE"] = init_db(get_db_uri(DevelopmentConfig()))


@db.command("create")
@click.pass_context
def create_db(ctx):
    create_tables_and_schema(ctx.obj["ENGINE"])


@db.command("interact")
@click.option("--profile/--no-profile", default=False)
@click.pass_context
def interact(ctx, profile):
    # these are injected into the IPython scope, but they appear to be unused.
    engine = ctx.obj["ENGINE"]  # noqa: F841

    if profile:
        enable_profiling()

    shell = InteractiveShellEmbed()
    shell()


@db.command("import-covidhub-project")
@click.option("--covidhub-db-secret", default="cliahub/cliahub_test_db")
@click.option("--rr-project-id", type=str, required=True)
@click.pass_context
def import_covidhub_project(ctx, covidhub_db_secret, rr_project_id):
    # these are injected into the IPython scope, but they appear to be unused.
    engine = ctx.obj["ENGINE"]

    import_project(engine, covidhub_db_secret, rr_project_id)
