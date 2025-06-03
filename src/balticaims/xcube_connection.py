from xcube.core.store import new_data_store
import requests

from balticaims.utils import get_logger


# TODO make configurable for other usages
S3_ENDPOINT_URL = "https://xcube.balticaims.eu/api/s3"
DATASETS_ENDPOINT_URL = "https://xcube.balticaims.eu/api/datasets"
DATA_STORE_ROOT = "datasets" # TODO potentially use "pyramids" here


class XcubeConnection:
    """
    Represent a connection to an xcube server.
    Can be queried for data.

    """
    def __init__(self) -> None:
        self._store = None
        self.logger = get_logger()

    def open_store(self):
        if not self._store:
            self._store = new_data_store(
                "s3",
                root=DATA_STORE_ROOT,
                storage_options={
                    "anon": True,
                    "client_kwargs": {
                        "endpoint_url": S3_ENDPOINT_URL,
                    }
                }
            )
        return self._store

    def get_ds(self, dataset_id):
        self.check_store()
        # TODO hardcoded zarr
        return self._store.open_data(dataset_id + ".zarr")

    def list_datasets(self):
        self.check_store()
        return self._store.get_data_ids()

    def check_store(self):
        if not self._store:
            raise RuntimeError(f"No data store initialized")

    def get_metadata(self, dataset_id):
        dataset_id = dataset_id.removesuffix(".zarr")
        self.logger.info(f"Requesting metadata for '{dataset_id}'")
        response = requests.get(f"{DATASETS_ENDPOINT_URL}/{dataset_id}")
        response.raise_for_status()
        return response.json()

    def get_dataset_names(self):
        self.logger.info(f"Requesting dataset list")
        response = requests.get(f"{DATASETS_ENDPOINT_URL}")
        response.raise_for_status()
        return response.json()
