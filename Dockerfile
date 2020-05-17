FROM jupyterhub/jupyterhub:latest
COPY . /ngshare/
RUN pip install /ngshare
USER 65535:65535
ENTRYPOINT ["python3", "-m", "ngshare"]
