FROM jupyterhub/jupyterhub:latest
COPY ngshare/ /ngshare/
USER 65535:65535
ENTRYPOINT ["python3", "/ngshare/ngshare.py"]
