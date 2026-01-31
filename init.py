import argparse
import downloader


def main():
    parser = argparse.ArgumentParser(description="Download animes from animeflv.net")
    parser.add_argument("anime", type=str, help="hyphen-separated anime name")
    parser.add_argument(
        "-b",
        "--browser",
        type=str,
        help="web browser to use",
        metavar="browser",
        required=False,
        choices=["safari", "chrome"],
        default="safari",
    )
    parser.add_argument(
        "-o",
        "--offset",
        type=int,
        help="start downloading from (and including) offset",
        metavar="offset",
        required=False,
        default=0,
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        help="max number of chapters to download (default is max)",
        metavar="limit",
        required=False,
        default=-1,
    )
    args = parser.parse_args()

    downloader.downloadAnime(
        args.anime, args.browser, offset=args.offset, limit=args.limit
    )


if __name__ == "__main__":
    main()
