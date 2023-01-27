FROM python:3.9.16-slim

RUN mkdir /var/www && chown www-data /var/www
WORKDIR /var/www
USER www-data
COPY --chown=www-data search-index.db search.py requirements.txt ./
COPY --chown=www-data templates/ ./templates/
RUN pip install -r requirements.txt

EXPOSE 8000/tcp
ENTRYPOINT ["/var/www/.local/bin/gunicorn", "--bind=0.0.0.0", "search:create_app"]
