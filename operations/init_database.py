

from Operations import Operations


import argparse


parser = argparse.ArgumentParser(
	prog="Posting service database initializer"
)
parser.add_argument(
	"--db",
	help="Path to database",
	dest="db_path",
	required=True
)
args = parser.parse_args()


ops = Operations(args.db_path)
ops.reinitialize_database()

