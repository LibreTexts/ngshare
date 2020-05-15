Development History
===================

The development of ``ngshare`` (backend) requires collaborating with frontend development and requires solving technical issues, so our plan breaks the development into different stages.

1. Develop ``vserver`` (see :doc:`project_structure`) with Unix file system APIs.
   This allows frontend to forward all file system calls (e.g. read file, write
   file) to another server. It allows frontend to test the idea when backend is
   implementing next stage.

2. Develop ``vserver`` with nbgrader APIs (e.g. create course, release assignment).
   After this the frontend can begin large changes to the exchange mechanism
   by replacing file system calls with nbgrader API calls. At this point no
   authentication is made.

3. Add authentication to ``vserver`` nbgrader APIs. To make things simple the
   frontend just needs to send the username, and the backend trusts what frontend
   does. During the first three stages, the backend can concurrently investigate
   how to set up a JupyterHub service.

4. Port ``vserver``'s nbgrader APIs to ``ngshare`` (final API server). There should be
   minimal effort in both backend and frontend as long as JupyterHub service can
   be set up correctly. The front end need to change the address of the server
   and send an API token instead of username; the backend need to copy the logic
   of ``vserver``.

5. Maintain ``ngshare``, fix any bugs and implement any features as frontend
   requests.

Currently we are at stage 5. 

