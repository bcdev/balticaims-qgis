import functools
from xcube.core.store import new_data_store


# TODO make configurable for other usages
ENDPOINT_URL = "https://xcube.balticaims.eu/api/s3"
DATA_STORE_ROOT = "datasets" # TODO potentially use "pyramids" here


class XcubeConnection:
    """
    Represent a connection to an xcube server.
    Can be queried for data.

    """
    def __init__(self) -> None:
        self._store = None

    def open_store(self):
        if not self._store:
            self._store = new_data_store(
                "s3",
                root=DATA_STORE_ROOT,
                storage_options={
                    "anon": True,
                    "client_kwargs": {
                        "endpoint_url": ENDPOINT_URL,
                    }
                }
            )
        return self._store

    def get_ds(self, dataset_id):
        self.check_store()
        return self._store.open_data(dataset_id)

    def list_datasets(self):
        self.check_store()
        return self._store.get_data_ids()

    def check_store(self):
        if not self._store:
            raise RuntimeError(f"No data store initialized")
