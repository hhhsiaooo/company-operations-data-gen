# The Data Generator for company operations data.
# Authors:
#   Hailey Hsiao, 2025


import argparse
import datetime as dt

from .logging import LOGGER
from .generate import (
    init_customer,
    weekly_scrape_product,
    daily_register_customer,
    daily_behavior_transaction,
)
from . import VERSION


def main():
    """The main program."""
    t_start: dt.datetime = dt.datetime.now()
    args: argparse.Namespace = parse_args()

    if args.command == "init":
        LOGGER.info("Generating the initial customer data.")
        init_customer()
    elif args.command == "weekly":
        LOGGER.info("Generating weekly product data.")
        weekly_scrape_product()
    elif args.command == "daily":
        LOGGER.info("Generating daily customer behavior data and transaction data.")
        daily_register_customer()
        daily_behavior_transaction()

    LOGGER.info(
        f"Finished at {dt.datetime.now()}. {dt.datetime.now() - t_start} elapsed."
    )


def parse_args() -> argparse.Namespace:
    """Parses the arguments."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Run the data generator."
    )
    parser.add_argument(
        "command",
        choices=["init", "weekly", "daily"],
        help="Choose the command to execute.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {VERSION}"
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
