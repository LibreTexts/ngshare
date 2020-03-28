FROM jupyterhub/jupyterhub

# Dependencies for nbgrader and JupyterHub setup.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY entrypoint.sh /

RUN useradd kale -d / -s /bin/bash
COPY jupyterhub_config.py .

COPY nbgrader_config.py /etc/jupyter/nbgrader_config.py
RUN touch /tmp/nbgrader.log && chmod a+rw /tmp/nbgrader.log

CMD ["/entrypoint.sh"]
