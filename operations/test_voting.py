

from Operations import Operations


import argparse


parser = argparse.ArgumentParser(
	prog="Voting microservice tester"
)
parser.add_argument(
	"--port",
	help="Voting API Port",
	dest="port",
	required=True,
	type=int
)
args = parser.parse_args()


ops = Operations(None)
ops.test_voting(args.port)

