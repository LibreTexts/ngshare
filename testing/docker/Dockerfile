FROM jupyterhub/jupyterhub

# Dependencies for nbgrader and JupyterHub setup.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY entrypoint.sh /

# Create exchange directory for nbgrader. Maybe no longer needed.
RUN mkdir -p /srv/nbgrader/exchange && chmod 777 /srv/nbgrader/exchange

RUN useradd kale -d / -s /bin/bash
COPY jupyterhub_config.py .

CMD ["/entrypoint.sh"]
