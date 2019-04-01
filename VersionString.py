def compare_version_strings(version_str1: str, version_str2: str, sep: str = ".", sep2: str = None) -> int:
    """
    Compares two strings containing version strings. Version strings should be of the following format
    xxx[sep]yyyy[sep] ..., where (xxxx) and (yyyy) should be numbers, and a separator, which can be the default ".", or
    can be set for each version string separately.

    Running examples would be:
    compare_version_strings("2.0.1", "02.00.01") -> should return 0, indicating they're equal
    compare_version_strings("2;1;0", "1;9;5", sep=";") -> should return 1, since the first version string is higher
    compare_version_strings("2,9,2", "2.9.3", sep=",", sep2=".") -> should return -1 since the first version string is
    smaller

    :param version_str1: first version string to compare
    :param version_str2: second version string to compare
    :param sep: default separator if sep2 is None, else the separator for the first version string
    :param sep2: separator for the second string
    :return: 0 if they're the same version, 1 if the first version string is higher, -1 if the first version string is
    smaller
    """

    # transform them in an array of ints, e.g. "2.00.01" -> [2, 0, 1]
    versions_1 = [int(v) for v in version_str1.split(sep)]
    versions_2 = [int(v) for v in version_str2.split(sep if not sep2 else sep2)]

    # if the versions are different in sizes, append 0 so they can compare to each other
    versions_1 += [0] * max(0, len(versions_2) - len(versions_1))
    versions_2 += [0] * max(0, len(versions_1) - len(versions_2))

    # When parsing int values, we could end up with a negative value. This is an error, since we don't want negative
    # versions on the version string.
    if len([v for v in versions_1 if v < 0]) > 0 or len([v for v in versions_2 if v < 0]) > 0:
        raise ValueError("Invalid value for version string. Should be higher or equal than 0.")

    # iterate over them, and compare them using lt and gt operators.
    for v1, v2 in zip(versions_1, versions_2):
        if v1 > v2:
            return 1
        if v2 > v1:
            return -1
    return 0
