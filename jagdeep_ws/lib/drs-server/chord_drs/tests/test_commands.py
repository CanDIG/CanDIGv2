from click.testing import CliRunner
from chord_drs.commands import ingest
from chord_drs.models import DrsObject, DrsBundle
from tests.conftest import (
    NON_EXISTENT_DUMMY_FILE,
    DUMMY_FILE,
    DUMMY_DIRECTORY,
)


# TODO: Issue with app context and backends. On hold for now
def test_ingest_fail(client_local):
    runner = CliRunner()
    result = runner.invoke(ingest, [NON_EXISTENT_DUMMY_FILE])

    assert result.exit_code == 1


def test_ingest(client_local):
    runner = CliRunner()
    result = runner.invoke(ingest, [DUMMY_FILE])

    filename = DUMMY_FILE.split('/')[-1]
    obj = DrsObject.query.filter_by(name=filename).first()

    assert result.exit_code == 0
    assert obj.name == filename
    assert obj.location

    result = runner.invoke(ingest, [DUMMY_DIRECTORY])

    filename = DUMMY_DIRECTORY.split('/')[-1]
    bundle = DrsBundle.query.filter_by(name=filename).first()

    assert result.exit_code == 0
    assert len(bundle.objects) > 0
