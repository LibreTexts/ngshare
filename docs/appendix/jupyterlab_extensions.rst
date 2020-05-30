Porting nbextensions to JupyterLab
==================================

We have made good progress porting the extensions to JupyterLab, but we are not quite finished. This document contains notes on the progress for all of the extensions.

Assignment List
---------------

The assignment list JupyterLab extension contains the exact same functionality and layout as the nbextension. After installation it can be launched by opening the command palette on the left side and searching for Assignment List

What's Done 
^^^^^^^^^^^
* All functionality
* Unit tests
* Styling

What's not Done 
^^^^^^^^^^^^^^^
* Could improve styling if wanted, but not necessary.
* The modals from validate assignment could use some better styling. Make styling of modals between assignment list and validate assignment consistent. 
* Contain the bootstrap CSS. It is affecting the styling of elements outside of the extension.

Code
^^^^
Files
"""""
* ``index.ts``

	* attaches the UI to the main work area

* ``assignmentlist.ts``

	* Contains all the logic necessary to display the assignments.

* ``handlers.py``

	* Defines the backend of the extension.
	* Uses the nbgrader ExchangeList, ExchangeFetchAssignment, ExchagneFetchFeedback, and ExchangeSubmit classes.  

Classes
"""""""
AssignmentList
	* Used to load and display the list of released, downloaded, and submitted assignments. 

Assignment
	* Creates the rows for each assignment. Each row consists of a link, a span element to display the name of the course, and a button.

Submission
	* Makes a submission row which consists of the timestamp and a link to a feedback file if there is any.

Notebook
	* Creates a row for each notebook in an assignment. The name of the notebook is a link to open the notebook and each row also contains a button to validate the notebook (run the tests for the notebook).

CourseList
	* Used to load and display the  course dropdown. 
	* When you click on a course it switches to to display the assignments for that course.

.. image:: ../extension_screenshots/assignment_list.jpg
   :width: 600

Create Assignment
-----------------
In Jupyter Notebooks, the extension put the UI in the cell toolbars. JupyterLab does not have cell toolbars, so we had to decide where to put the interface. We decided on a side panel which shows the nbgrader assignment information for the active notebook.

What’s Done
^^^^^^^^^^^
* Everything (extension, styling, tests, etc.)

What’s Not Done
^^^^^^^^^^^^^^^
* Nothing

Code
^^^^
Files
"""""
* ``index.ts``

	* attaches the UI to a side panel.
* ``extension.ts``

	* contains the UI elements.
* ``model.ts``

	* contains the logic which acts as an intermediary between the UI and the notebook cell metadata.

Classes
"""""""
CreateAssignmentWidget
	* A container for the UI, which can theoretically be attached to any widget, not just a side panel
	* Listens to determine which notebook is the current notebook
	* Shows the NotebookWidget for the current notebook

NotebookWidget
	* Contains the UI associated with a notebook
	* Has a NotebookHeaderWidget at the top and a NotebookPanelWidget which takes up the remaining space
NotebookHeaderWidget
	* Currently, only contains the total points for the assignment
NotebookPanelWidget
	* Contains a list of CellWidgets to show the assignment information for each cell
	* Listens to changes in the notebook cell list
	* Adds, removes, reorders, or highlights CellWidgets to synchronize with the notebook
CellWidget
	* Contains the UI showing the nbgrader assignment information for one cell
	* Reads and writes nbgrader data in the cell metadata

.. image:: ../extension_screenshots/create_assignment.jpg
   :width: 600

Course List
-----------
Same functionality and layout as the course list nbextension. After installation it can be launched by opening the command palette on the left side and searching for Course List

What’s Done
^^^^^^^^^^^
* All functionality is there.
* Unit tests
* Some styling

What’s Not Done
^^^^^^^^^^^^^^^
* Could use more styling 

Code
^^^^
Files
"""""
* ``index.ts``

	* attaches the UI to the main work area.
* ``courselist.ts``

	* Contains all the logic necessary to display the courses. 
* ``handers.py``

	* Defines the backend of the extension.

Classes
"""""""
CourseList
	* Loads and displays the list of courses.
	* The name of each course is a link to the formgrader for that course.

.. image:: ../extension_screenshots/course_list.jpg
   :width: 600

Formgrader
----------
No work has been done on formgrader. This extension is very different from the others since it is complex and has a stand-alone interface.

What’s Done
^^^^^^^^^^^
* Nothing

What’s Not Done
^^^^^^^^^^^^^^^
* Everything

Possible Plan
^^^^^^^^^^^^^
* Add launcher and/or command palette entry
* Open formgrader UI in the main area
* Edit appropriate hyperlinks in the UI to open items in JupyterLab instead of Jupyter

Validate Assignment
-------------------
What’s Done
^^^^^^^^^^^
* All functionality
* Unit tests
* Some styling

What’s Not Done
^^^^^^^^^^^^^^^
* Styling

  * The modals could use some better styling. 
  * Make styling of modals between assignment list and validate assignment consistent. 

.. image:: ../extension_screenshots/validate_assignment.jpg
   :width: 600
