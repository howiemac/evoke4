"""
evoke library interface


(IHM April 2007)
"""

# make everything visible as base.lib
from library import * 
from deprecated import *
from error import Error
from permit import Permit, Condition, Conditionfn

from DATE import DATE
from STR import TAG, STR, CHAR
from TEXT import TEXT
from INT import INT, SMALLINT, TINYINT
from FLOAT import FLOAT, DOUBLE
from MONEY import MONEY
from TIME import TIME
from FLAG import FLAG
from REL import REL
from BLOB import BLOB
from bug import send_error
