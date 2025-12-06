def get_source(root_server, source_name):
    """Get the data from the main Fract server, then return source data."""
    
    # Import the requests library with error handling.
    try:
        import requests
    except:
        print("\x1b[31mFailed to load requests, perhaps you didn't install it?\nTo install: \x1b[33mpip install requests\x1b[31m.\x1b[0m")
        exit(1)

    # Try to get the data, with error handling.
    try:
        r = requests.get(root_server+"/main.json")
    except Exception as e:
        print(f"\x1b[31mError connecting to main server:\x1b0m {3}")
        exit(1)
    
    data = r.json()

    # Make sure source exists.
    try:
        data = data[source_name]
    except:
        print("\x1b[31mSource not found.\x1b[0m")
        exit(1)

    # Make sure all the source data exists.
    try:
        name = data["name"]
        url = data["url"]
    except:
        print("\x1b[31mMissing source data (source exists but is missing data).\x1b[0m")
        exit(1)

    return data

def get_pkgdata(source_url, package_name, version=None):
    """Get package data from source server."""

    # Import the requests library with error handling.
    try:
        import requests
    except:
        print("\x1b[31mFailed to load requests, perhaps you didn't install it?\nTo install: \x1b[33mpip install requests\x1b[31m.\x1b[0m")
        exit(1)

    # Get the data from source with error handling.
    try:
        r = requests.get(source_url+"/main.json")
    except Exception as e:
        print(f"\x1b[31mError connecting to source server:\x1b0m {3}")
        exit(1)
    
    data = r.json()

    # Check data version and parse it accordingly.
    if data["schema_version"] == 1:
        print("\x1b[31mError: source has unsupported outdated schema version.\x1b[0m")
        exit(1)

    elif data["schema_version"] == 2:
        # Get package data and make sure it exists.
        try:
            pkg_data = data["packages"][package_name]
        except:
            print("\x1b[31mPackage does not exist.\x1b[0m")
            exit(1)

        # If no version chosen, default to latest.
        if not version:
            version = pkg_data["latest"]

        # Import osarch with error handling.
        try:
            from osarch import detect_system_architecture
        except:
            print("\x1b[31mFailed to load the library osarch, perhaps you haven't installed it?\nTo install it: \x1b[33mpip install osarch\x1b[31m.\x1b[0m")
            exit(1)

        arch = detect_system_architecture()[1]

        if arch in pkg_data["versions"][version]:
            return pkg_data["versions"][version][arch]
        else:
            return pkg_data["versions"][version]["any"] 

    else:
        print("\x1b[31mUnknown schema version.\x1b[31m")
        exit(1)

