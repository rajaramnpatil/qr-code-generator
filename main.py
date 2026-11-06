"""Generate a QR code from a URL and save it as a PNG image."""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import qrcode
import validators
from dotenv import load_dotenv


def setup_logging():
    """Send application logs to the terminal and Docker logs."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def parse_arguments():
    """Read the URL from the command line."""
    parser = argparse.ArgumentParser(
        description="Generate a QR code for a valid HTTP or HTTPS URL."
    )
    parser.add_argument(
        "--url",
        default="https://github.com/rajaramnpatil",
        help="URL to encode (default: https://github.com/rajaramnpatil)",
    )
    return parser.parse_args()


def is_valid_url(url):
    """Check that the URL is valid and uses HTTP or HTTPS."""
    return (
        url.lower().startswith(("http://", "https://"))
        and validators.url(url) is True
    )


def create_directory(path):
    """Create the output directory, including any missing parent folders."""
    path.mkdir(parents=True, exist_ok=True)


def generate_qr_code(data, path, fill_color="red", back_color="white"):
    """Generate and save a QR code, allowing errors to reach main()."""
    if not is_valid_url(data):
        raise ValueError("Provide a valid URL starting with http:// or https://.")

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=5,
    )
    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color=fill_color,
        back_color=back_color,
    )

    with path.open("wb") as qr_file:
        image.save(qr_file, format="PNG")

    logging.info("QR code successfully saved to %s", path)


def main():
    """Load configuration, generate a QR code, and return an exit code."""
    setup_logging()
    load_dotenv()
    args = parse_arguments()

    url = args.url.strip()
    qr_directory = Path(os.getenv("QR_CODE_DIR", "qr_codes"))
    fill_color = os.getenv("FILL_COLOR", "black")
    back_color = os.getenv("BACK_COLOR", "white")

    try:
        if not is_valid_url(url):
            raise ValueError(
                "Provide a valid URL starting with http:// or https://."
            )

        create_directory(qr_directory)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = qr_directory / f"QRCode_{timestamp}.png"

        generate_qr_code(
            data=url,
            path=output_path,
            fill_color=fill_color,
            back_color=back_color,
        )
        return 0

    except ValueError as error:
        logging.error("Invalid URL or QR code configuration: %s", error)
    except OSError as error:
        logging.error("Unable to create or write the QR code file: %s", error)
    except Exception:
        logging.exception("Unexpected error while generating the QR code")

    return 1


if __name__ == "__main__":
    sys.exit(main())