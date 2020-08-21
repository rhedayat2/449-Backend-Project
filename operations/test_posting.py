

from Operations import Operations


import argparse


parser = argparse.ArgumentParser(
	prog="Posting microservice tester"
)
parser.add_argument(
	"--port",
	help="Posting API Port",
	dest="port",
	required=True,
	type=int
)
args = parser.parse_args()


ops = Operations(None)
ops.test_posting(args.port)

