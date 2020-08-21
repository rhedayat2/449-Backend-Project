

from Operations import Operations


import argparse


parser = argparse.ArgumentParser(
	prog="Posting service database initializer"
)
parser.add_argument(
	"--posting-port",
	help="Posting port",
	dest="posting_port",
	required=True,
	type=int
)
parser.add_argument(
	"--voting-port",
	help="Voting port",
	dest="voting_port",
	required=True,
	type=int
)


args = parser.parse_args()


ops = Operations(None)
ops.populate_database(args.posting_port, args.voting_port)

