#!/usr/bin/env python

from airunner.app_installer import AppInstaller
from airunner.setup_database import setup_database


def main():
    setup_database()
    AppInstaller()


if __name__ == "__main__":
    main()
