# __import__("pysqlite3")

# import sys

# sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# import sqlite3

# print("Patched SQLite Version:", sqlite3.sqlite_version)
import sys
import platform

# Only patch SQLite on Linux (Lambda/Docker)
if platform.system() != "Windows":
    try:
        __import__("pysqlite3")
        sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
        print("Using pysqlite3")
    except ImportError:
        print("pysqlite3 not available, using default sqlite3")
else:
    print("Windows detected - using default sqlite3")