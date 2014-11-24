"""
evoke base database interface
"""

from data import makeDataClass, RecordNotFoundError
from DB import execute, init_db
from schema import *
from patch import pre_schema