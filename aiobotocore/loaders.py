import os

from botocore.loaders import Loader


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

    pass
