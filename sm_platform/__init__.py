"""Project package initialization.

If PyMySQL is installed, configure it as MySQLdb so Django can use it
without requiring mysqlclient (easier on Windows).
"""

try:
	import pymysql

	pymysql.install_as_MySQLdb()
except Exception:
	# It's okay if PyMySQL isn't installed in development without MySQL
	pass

