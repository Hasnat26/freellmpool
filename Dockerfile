# Industrial RFQ Intelligence — minimal CLI container.
#
# This image packages the native industrial-rfq-intelligence CLI.
# It does not expose a network service and does not contain production
# credentials or autonomous procurement/control capabilities.

FROM python:3.14-alpine@sha256:05b2b8b732ecd268fee8727a369f936f022d1321b59befd13c30ede22769dcdc

WORKDIR /app
RUN apk upgrade --no-cache
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .     && python -m pip uninstall --yes pip setuptools wheel

RUN adduser -D -u 10001 industrial
USER industrial

ENTRYPOINT ["industrial-rfq-intelligence"]
CMD ["--help"]
