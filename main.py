# Imports
import argparse
import os
import shutil

# Config
import build_config as config

# __name__ guard to ensure program isnt being imported.
if __name__ == "__main__":
    # Argument parsing using argparse.
    parser = argparse.ArgumentParser(
            prog="Fract",
            description="The Fizz appstore.\nMade by Linux. Made for Linux.",
            epilog="Made by Fizz Org.\nGitHub: https://github.com/Fizz-Org/.")

    parser.add_argument("-S", "--install", dest="install", action='store_true', help="Download and install a package.")
    parser.add_argument("-D", "--download", dest="download", action='store_true', help="Download a package.")
    parser.add_argument("-R", "--remove", dest="remove", action="store_true", help="Removes a package.")
    parser.add_argument("package", nargs="?", help="The package name: <source>/<further path and name>.")
    parser.add_argument("-v", "--version", dest="version", help="Choose witch version you want.")
    args = parser.parse_args()

    # Devmode setup.
    if config.DEVELOPER_MODE:
        print("\x1b[33mDeveloper mode: active.\x1b[0m")
        CACHE_DIR = "cache"
    else:
        CACHE_DIR = os.path.expanduser(config.CACHE_FOLDER)

    # Make sure tat CACHE_DIR exists.
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # Download a package.
    if args.download:
        import src.data_fetcher as df 
        import src.downloader as dl

        # Ensures a package is specified
        if not args.package:
            print("\x1b[31mMust specify a package.\x1b[0m")
            exit(1)
        
        # Format source and package name.
        source_name = args.package.split("/")[0]
        package_name = "/".join(args.package.split("/")[1:])

        # Grab source data from root server.
        source_data = df.get_source(config.ROOT_SERVER, source_name)

        # Grab package data (such as file location):
        pkg_data = df.get_pkgdata(source_data["url"], package_name, version=args.version)

        # Download package (and check sha256).
        filepath = dl.fetch_package(CACHE_DIR, source_data["url"], pkg_data)
        
        # Copy package binary to current working directory.
        shutil.copy(filepath, os.getcwd())
   
    else:
        print("\x1b[33mUse with the -h tag for help menu.\x1b[0m")

# Exit with a warning and an error if program is imported.
else:
    print("\x1b[31mDon't import this program, it is not meant to be imported.\x1b[0m")
    exit(1)
