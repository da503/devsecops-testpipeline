FROM python@sha256:2d97f6910b16bd338d3060f261f53f144965f755599aab1acda1e13cf1731b1b

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000
RUN useradd --create-home appuser
USER appuser
CMD ["python", "app.py"]

# Note: python:3.9-slim is used deliberately as a slightly dated base image
# so that Trivy's image scan has known OS-package CVEs to surface in the
# pipeline demo. A hardened build would pin a current, minimal (or distroless)
# base image and drop to a non-root user - see docs/hardening-notes.md.
