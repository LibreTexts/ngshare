System Architecture Overview
============================

``ngshare`` is intended to run as a Kubernetes pod and service outside JupyterHub. In a Kubernetes setup, ngshare is proxied by JupyterHub's proxy service and can be accessed from any JupyterHub user pod. It uses the Hub for authentication.

.. image:: ../assets/architecture5b.svg
    :alt: System Architecture Diagram
    :align: center

