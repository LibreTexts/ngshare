# ngshare
[nbgrader](https://github.com/jupyter/nbgrader) sharing service.

**This service is under development. Use this at your own risk.**

Click [here](#installation-and-setup) for installation instructions.

<img src="ngshare/favicon.png" width="64px" />

## What is ngshare?
[ngshare](https://github.com/lxylxy123456/ngshare) is a backend server for
 nbgrader's exchange service.

[nbgrader](https://github.com/jupyter/nbgrader) is a Jupyter notebooks extension
 for grading running on JupyterHub, but it does not work well in distributed
 setup of JupyterHub like in Kubernetes, because the file systems exchange uses
 are not connected between containers. 

To solve this problem, we are letting exchange to gather all information it
 needs from a set of REST APIs, which is implemented by ngshare. This server
 will be a JupyterHub managed service.

We are currently working on the frontend (nbgrader) in
 [an nbgrader fork](https://github.com/lxylxy123456/nbgrader) to make it use
 this API (ngshare, or "backend").

## Why ngshare?
The major problem we need to solve is that nbgrader exchange mechanism uses
 a directory in Unix file system (exchange directory), which cannot be shared
 between containers when JupyterHub runs on Kubenetes.

We brainstormed a few possible solutions before starting the ngshare project:
* hubshare
	* [hubshare](https://github.com/jupyterhub/hubshare) is a directory sharing
	 service for JupyterHub. 
	* Pros
		* Universal solution that can be integrated with nbgrader.
		* Similar service desired by nbgrader developer 
		 (see
		 [jupyter/nbgrader#659](https://github.com/jupyter/nbgrader/issues/659))
	* Cons
		* Lots of work to implement HubShare. 
		* nbgrader exchange mechanism need to be reworked.
		* Too generic, does not have permission control specific to classes &
		 assignment. (see
		 [this comment](https://github.com/jupyter/nbgrader/issues/659#issuecomment-431762792))
* NFS
	* Another solution is to let every container access a shared file system
	 through NFS (Network File System).
	* Pros
		* Very doable. Does not "require" input from the Jupyter community.
	* Cons
		* Not a universal solution.
* Kubernetes Persistent Volume Claim
	* [Kubernetes Persistent Volume Claim](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims)
	 allows containers to request shared file systems.
	* Pros
		* More universal than the NFS solution. Does not "require" input from
		 the Jupyter community.
	* Cons
		* Difficult to work around limitations regarding multiple writers per
		 volume. Need to find a way to have correct permissions for students and
		 instructors.

The best solution we think is the first one, but the generic problem still need
 to be solved. So we decided to find a fourth solution, which is creating a
 service similar to hubshare but more specialized for nbgrader.
* ngshare
	* ngshare implements a set of [REST APIs](api-specifications.md) designed
	 for nbgrader exchange mechanism.
	* Pros
		* Universal solution that can be integrated with nbgrader.
		* **Fully controlled APIs by this project.**
	* Cons
		* Work needs to be done to implement ngshare.
		* nbgrader exchange mechanism needs to be reworked. 

## Developing ngshare
The development of ngshare (backend) requires collaborating with frontend
 development and requires solving technical issues, so our plan breaks the
 development into different stages.
1. Develop vserver (see [#Structure](#Structure)) with Unix file system APIs.
 This allows frontend to forward all file system calls (e.g. read file, write
 file) to another server. It allows frontend to test the idea when backend is
 implementing next stage.
2. Develop vserver with nbgrader APIs (e.g. create course, release assignment).
 After this the frontend can begin large changes to the exchange mechanism
 by replacing file system calls with nbgrader API calls. At this point no
 authentication is made.
3. Add authentication to vserver nbgrader APIs. To make things simple the
 frontend just needs to send the username, and the backend trusts what frontend
 does. During the first three stages, the backend can concurrently investigate
 how to set up a JupyterHub service.
4. Port vserver's nbgrader APIs to ngshare (final API server). There should be
 minimal effort in both backend and frontend as long as JupyterHub service can
 be set up correctly. The front end need to change the address of the server
 and send an API token instead of username; the backend need to copy the logic
 of vserver.
5. Maintain ngshare, fix any bugs and implement any features as frontend
 requests.

Currently we are at stage 5. 

## What can I use it for?
You can use ngshare if you
* Need to run nbgrader on a distributed set up (probably using
 [lxylxy123456/nbgrader](https://github.com/lxylxy123456/nbgrader))
* Have something similar to nbgrader that also needs an API to manage courses,
 homework submissions and feedbacks, etc.
* Want to learn Flask, SQLAlchemy, or Tornado Web Server. 

## Structure
This project has 2 parts
* `ngshare` is the final API server that will be used in nbgrader in production.
 Written as Tornado Web Server and using SQLAlchemy.
	* `vngshare` stands for Vserver-like Notebook Grader Share. It has the same
	 functionality as `ngshare` but is built as a stand-alone server (does not
	 require JupyterHub environment), which makes testing easier.
* `vserver` is a simple and **vulnerable** API server, written in Flask, that
 allows testing the project structurte and development of frontend without
 waiting for backend.
	* Mar 7, 2020: Since `ngshare` is already mature, we decided to no longer
	 support `vserver` anymore. `vngshare` does almost the exact same thing
	 as `ngshare`. So the current version of `vserver` should conform to the API
	 documentation at Git version
	 [`890c4b21`](https://github.com/lxylxy123456/ngshare/blob/890c4b2187acc6f592a63b8df9db003226ce2b1e/api-specifications.md).
	* See [/vserver](/vserver)

The database structure is documented in [ngshare/database](ngshare/database).

## APIs
The API specifications for `ngshare` are available in
 [`api-specifications.md`](api-specifications.md).

## Installation and setup
* See [/testing](/testing#testing-setup) for setting up `ngshare` and `JupyterHub` for simple testing.

To install `ngshare` onto your cluster with some default values, simply do:

`helm install ngshare helmchart/ngshare`

We recommend using some configurations manually. Here's a sample `config.yaml` file:
```yaml
deployment:
  resources:
    limits:
      cpu: 100m
      memory: 128Mi

ngshare:
  # You may omit this, but the token will be randomly generated.
  # It's recommended to specify an API token here.
  hub_api_token: ENTER_TOP_SECRET_TOKEN_HERE

pvc:
  # Amount of storage for ngshare
  storage: 1Gi
```
For a reference of all the options you can specify, check [here](/helmchart/ngshare/values.yaml).

After you install, you should see a message like this:
```
Congrats, ngshare should be installed!
To get started, add the following to your JupyterHub helm chart's values:

hub:
  extraConfig:
    ngshare.py: |
      c.JupyterHub.services.append({
        'name': 'ngshare',
        'url': 'http://ngshare:8080',
        'api_token': 'a4IHeiHZuswZrmYbWxSGpLZs3x0pXVxa'})
```
You should:
1. Follow the first part of the instructions, and add the `extraConfig` part into your JupyterHub's helm chart.
2. Modify your singleuser image to install our fork of nbgrader, and add some configuration to your default `nbgrader_config.py` so it uses ngshare. You can add something like this to your singleuser Dockerfile:
```dockerfile
RUN pip install git+https://github.com/lxylxy123456/nbgrader@exchange_server && \
jupyter nbextension install --symlink --sys-prefix --py nbgrader && \
jupyter nbextension enable --sys-prefix --py nbgrader && \
jupyter serverextension enable --sys-prefix --py nbgrader

COPY nbgrader_config.py /etc/jupyter/
```
with an accompanying `nbgrader_config.py` like this:
```python
from nbgrader.exchange import ngshare
c = get_config()
c.ExchangeFactory.exchange = ngshare.Exchange
c.ExchangeFactory.fetch_assignment = ngshare.ExchangeFetchAssignment
c.ExchangeFactory.fetch_feedback = ngshare.ExchangeFetchFeedback
c.ExchangeFactory.release_assignment = ngshare.ExchangeReleaseAssignment
c.ExchangeFactory.release_feedback = ngshare.ExchangeReleaseFeedback
c.ExchangeFactory.list = ngshare.ExchangeList
c.ExchangeFactory.submit = ngshare.ExchangeSubmit
c.ExchangeFactory.collect = ngshare.ExchangeCollect
```
Afterwards, the setup should be complete.

## Demo
If you are configuring our project correctly, you should be able to run this demo.
1. Setup a clean environment using JupyterHub + nbgrader + ngshare (debug mode). You can use the [minikube testing setup](/testing#testing-setup) to do it easily.
2. Login as user "user". All usernames are login-able with any passwords.
3. Go to "Control Panel" at upper right corner, then Services -> ngshare
4. Click on "init with test data". You should see
	`{"success": true, "message": "done"}`.
5. Login as user "kevin".
6. Create a new file with New -> Text File, name it `nbgrader_config.py` and
	with the following content:
```
c = get_config()
c.CourseDirectory.course_id = "course1"
```
7. Go to "Control Panel", click on "Stop My Server"
8. Click on "Start My Server"
9. Go to "Formgrader".
10. Click "Add new assignment..."
11. Click on the name of the assignment you just added
12. New -> Notebook -> Python 3, and edit the notebook as in normal nbgrader
	1. Add some code to the block
	2. View -> Cell Toolbar -> Create Assignment
	3. Select "Autograded answer"
	4. ...
	5. Save notebook
13. Click "Generate" in Formgrader
14. Click "Release" in Formgrader
15. Login as user "lawrence" (you may want to use incognito mode).
16. Go to "Assignments" tab
17. Click "Fetch" for the new assignment (the one that is not "challenge")
18. Do your homework.
19. Click "Submit".
20. Login as user "kevin".
21. Click "Collect" in Formgrader. 
22. You should see "1" under "# Submissions". Click on this number. 
23. Click "Autograde"
24. Click Student Name, and then the notebook name, then write some feedback and
	click "Next".
25. Go back to "Manage Assignments"
26. Click "Generate Feedback", and "Release Feedback" in order.
27. Login as user "lawrence".
28. Under "Assignments", click "Fetch Feedback"
29. You should see "(view feedback)" on the right of the time stamp, but do not
	click on it. 
30. Go to "Files" tab and go to `<assignment name>/feedback/<timestamp>`, then
	you can view the html feedbacks. 

### Youtube Video Demo
http://www.youtube.com/watch?v=iiaVpKLj89c

[![Youtube Video Demo](http://img.youtube.com/vi/iiaVpKLj89c/0.jpg)](http://www.youtube.com/watch?v=iiaVpKLj89c)

## Database migrations
ngshare uses [Alembic](https://alembic.sqlalchemy.org/) to manage database
 migrations.

For development, first install ngshare as a repo using
 `pip3 install . --user --upgrade`, then initialize the database using
 `alembic upgrade head` (the path to database is defined in `alembic.ini`,
 which is `sqlite:////tmp/ngshare.db` by default).

After changing database structure, use `pip3 install . --user --upgrade` and
 then `alembic revision --autogenerate -m "message"` to automatically detect
 changes, then `alembic upgrade head` to upgrade database structures.

