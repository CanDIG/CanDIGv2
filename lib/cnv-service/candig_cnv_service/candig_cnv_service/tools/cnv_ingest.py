import sys
import os
import argparse

from sqlalchemy.exc import IntegrityError

from candig_cnv_service.tools.ingester import Ingester
from candig_cnv_service.api.exceptions import FileTypeError


def main(args=None):
    """
    Main script for ingesting CNV files through the CLI. Call this script
    along with all the arguments needed. patient, sample and file are all
    required.
    """
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser("Run Candig CNV Ingest Tool")
    parser.add_argument("patient", help="Patient UUID (must already exist)")
    parser.add_argument("sample", help="Sample ID (must already exist)")
    parser.add_argument("file", help="Location of CNV file")
    parser.add_argument(
        "--database",
        help="Location of database",
        default=os.getcwd()+"/data/cnv_service.db"
        )
    parser.add_argument(
        "--sequential",
        help="Enables sequential uploading on ingest failure",
        default=False
        )
    args, _ = parser.parse_known_args()

    try:
        CNV = Ingester(
            database=args.database,
            patient=args.patient,
            sample=args.sample,
            cnv_file=args.file
            )
    except FileTypeError as FTE:
        print(FTE.args[0])
        quit()
    except TypeError:
        print("Invalid DB location")
        quit()

    try:
        CNV.upload()
    except IntegrityError as IE:
        print(IE.args)
        if args.sequential:
            print("Running Sequential Upload")
            CNV.upload_sequential()


if __name__ == "__main__":
    main()
