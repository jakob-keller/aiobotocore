import asyncio
import os

from botocore.exceptions import UnknownServiceError
from botocore.loaders import Loader, instance_cache


def create_loader(search_path_string=None):
    """Create a Loader class.

    This factory function creates a loader given a search string path.

    :type search_string_path: str
    :param search_string_path: The AWS_DATA_PATH value.  A string
        of data path values separated by the ``os.path.pathsep`` value,
        which is typically ``:`` on POSIX platforms and ``;`` on
        windows.

    :return: A ``Loader`` instance.

    """
    if search_path_string is None:
        return AioLoader()
    paths = []
    extra_paths = search_path_string.split(os.pathsep)
    for path in extra_paths:
        path = os.path.expanduser(os.path.expandvars(path))
        paths.append(path)
    return AioLoader(extra_search_paths=paths)


class AioLoader(Loader):
    """Find and load data models.

    This class will handle searching for and loading data models.

    The main method used here is ``load_service_model``, which is a
    convenience method over ``load_data`` and ``determine_latest_version``.

    """

    @instance_cache
    def load_service_model(self, service_name, type_name, api_version=None):
        """Load a botocore service model

        This is the main method for loading botocore models (e.g. a service
        model, pagination configs, waiter configs, etc.).

        :type service_name: str
        :param service_name: The name of the service (e.g ``ec2``, ``s3``).

        :type type_name: str
        :param type_name: The model type.  Valid types include, but are not
            limited to: ``service-2``, ``paginators-1``, ``waiters-2``.

        :type api_version: str
        :param api_version: The API version to load.  If this is not
            provided, then the latest API version will be used.

        :type load_extras: bool
        :param load_extras: Whether or not to load the tool extras which
            contain additional data to be added to the model.

        :raises: UnknownServiceError if there is no known service with
            the provided service_name.

        :raises: DataNotFoundError if no data could be found for the
            service_name/type_name/api_version.

        :return: The loaded data, as a python type (e.g. dict, list, etc).
        """
        return asyncio.create_task(
            self._load_service_model(service_name, type_name, api_version)
        )

    async def _load_service_model(
        self, service_name, type_name, api_version=None
    ):
        # Wrapper around the load_data.  This will calculate the path
        # to call load_data with.
        known_services = self.list_available_services(type_name)
        if service_name not in known_services:
            raise UnknownServiceError(
                service_name=service_name,
                known_service_names=', '.join(sorted(known_services)),
            )
        if api_version is None:
            api_version = self.determine_latest_version(
                service_name, type_name
            )
        full_path = os.path.join(service_name, api_version, type_name)
        model = self.load_data(full_path)

        # Load in all the extras
        extras_data = self._find_extras(service_name, type_name, api_version)
        self._extras_processor.process(model, extras_data)

        return model
