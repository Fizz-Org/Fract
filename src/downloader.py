def get_source(root_server, source_name):
    """Get the data from the main Fract server, then return source data."""
    
    # Import the requests library with error handing.
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
