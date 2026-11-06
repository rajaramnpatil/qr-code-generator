"""Tests for URL validation, QR generation, and CLI behavior."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from main import create_directory, generate_qr_code, is_valid_url


SCRIPT = Path(__file__).resolve().parents[1] / "main.py"


@pytest.mark.parametrize(
    "url",
    [
        "https://www.njit.edu",
        "http://example.com",
        "https://github.com/rajaramnpatil/qr-code-generator",
    ],
)
def test_valid_url(url):
    assert is_valid_url(url) is True


@pytest.mark.parametrize(
    "url",
    ["", "invalid-url", "example.com", "ftp://example.com"],
)
def test_invalid_url(url):
    assert is_valid_url(url) is False


def test_create_directory(tmp_path):
    directory = tmp_path / "output" / "qr_codes"

    create_directory(directory)
    create_directory(directory)

    assert directory.is_dir()


def test_generate_valid_png(tmp_path):
    output = tmp_path / "qr.png"

    generate_qr_code(
        "https://www.njit.edu",
        output,
        fill_color="black",
        back_color="white",
    )

    with Image.open(output) as image:
        assert image.format == "PNG"
        image.verify()


def test_invalid_url_does_not_create_file(tmp_path):
    output = tmp_path / "invalid.png"

    with pytest.raises(ValueError):
        generate_qr_code("invalid-url", output)

    assert not output.exists()


def run_cli(tmp_path, url):
    """Run the real application with isolated output and configuration."""
    environment = os.environ.copy()
    environment.update(
        {
            "QR_CODE_DIR": str(tmp_path / "output"),
            "FILL_COLOR": "black",
            "BACK_COLOR": "white",
            "PYTHON_DOTENV_DISABLED": "1",
        }
    )

    return subprocess.run(
        [sys.executable, str(SCRIPT), "--url", url],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_cli_success(tmp_path):
    result = run_cli(tmp_path, "https://www.njit.edu")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "QR code successfully saved" in result.stdout

    files = list((tmp_path / "output").glob("QRCode_*.png"))
    assert len(files) == 1

    with Image.open(files[0]) as image:
        rgb_image = image.convert("RGB")
        colors = {
            rgb_image.getpixel((x, y))
            for y in range(rgb_image.height)
            for x in range(rgb_image.width)
        }
        assert colors == {(0, 0, 0), (255, 255, 255)}


def test_cli_invalid_url(tmp_path):
    result = run_cli(tmp_path, "invalid-url")

    assert result.returncode == 1
    assert not list(tmp_path.rglob("*.png"))