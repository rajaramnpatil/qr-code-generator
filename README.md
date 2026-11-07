# QR Code Generator

A Python command-line application that converts an HTTP or HTTPS URL into a
timestamped PNG QR code. The Docker image uses Python 3.12 slim and runs the
application as a non-root user.

- [GitHub repository](https://github.com/rajaramnpatil/qr-code-generator)
- [Docker Hub image](https://hub.docker.com/r/rajaramnpatil/qr-code-generator-app)
- [GitHub Actions runs](https://github.com/rajaramnpatil/qr-code-generator/actions)

## Run the published image

```bash
docker pull rajaramnpatil/qr-code-generator-app:latest

docker run --rm \
  -e QR_CODE_DIR=/app/qr_codes \
  -e FILL_COLOR=black \
  -e BACK_COLOR=white \
  -v qr-generator-output:/app/qr_codes \
  rajaramnpatil/qr-code-generator-app:latest \
  --url https://github.com/rajaramnpatil/qr-code-generator
```

The app logs the PNG path and exits with code `0` on success. The named volume
`qr-generator-output` keeps the PNG after the container is removed.

List the saved files:

```bash
docker run --rm \
  -v qr-generator-output:/app/qr_codes \
  --entrypoint ls \
  rajaramnpatil/qr-code-generator-app:latest \
  -l /app/qr_codes
```

## Configuration

| Environment variable | Default | Purpose |
|---|---|---|
| `QR_CODE_DIR` | `qr_codes` | Directory where PNG files are saved |
| `FILL_COLOR` | `red` | QR code color |
| `BACK_COLOR` | `white` | Background color |

Use `--url` to set the URL encoded in the QR code.

## Build locally

Run from the repository root:

```bash
docker build -t qr-code-generator-app .
docker run --name qr-generator-local qr-code-generator-app --url https://www.njit.edu
docker logs qr-generator-local
docker cp qr-generator-local:/app/qr_codes ./generated_qr_codes
docker rm qr-generator-local
```

## Run the tests

In an active Python virtual environment, run:

```bash
python -m pip install -r requirements.txt
python -m pytest tests/ -v
```

GitHub Actions runs the tests on Python 3.14, builds the Docker image, checks
that the container runs as a non-root user, and verifies the generated PNG.