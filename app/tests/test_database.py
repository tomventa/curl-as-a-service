from app.database import config, get_db
from pymongo.database import Database
from bson.raw_bson import RawBSONDocument
from bson import CodecOptions

def test_database_config():
    assert len(config['host']) > 0
    assert isinstance(config['port'], int)
    assert len(config['user']) > 0
    assert len(config['password']) > 0
    assert len(config['database']) > 0

def test_get_db():
    # This is the real database, tests should not write or read from it
    db = get_db()
    assert isinstance(db, Database)
    # Perform a non-intrusive ping
    options = CodecOptions(RawBSONDocument)
    result = db.command("ping", codec_options=options)
    assert isinstance(result, RawBSONDocument)