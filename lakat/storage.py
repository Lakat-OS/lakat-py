from setup import storage

# clear db and start a new db
def restart_db():
    return storage.db_interface.restart()


def restart_db_with_name(name: str):
    return storage.db_interface.restart(name=name)