Requirements
============

User Stories
------------
* As a campus IT service provider, I want to be able to run nbgrader on kubernetes, so the teachers can easily direct students to use nbgrader on the service I provide in their programming classes.
* As a programming class teacher, I want nbgrader to be able to run on the JupyterLab interface. It would give students access to a more user-friendly programming environment.
* As a course instructor, I want nbgrader to warn me when I’m about to publish an edited assignment from “preview” mode in order to minimize the risk of accidentally releasing something I wrote for testing purposes.
* As a course instructor / TA, I want a button that runs the nbgrader autograder for all students’ submissions so that I don’t have to click “autograde” for every submission.
* As a course instructor / TA, I want to be able to manually grade one question across all submissions so that I can grade question by question instead of submission by submission.
* As a course instructor / TA, I want to be able to write a rubric before grading and then use it to quickly assign points to a problem, instead of typing in grade and feedback for each student’s submission. This functionality can be similar to what Gradescope provides.
* As a course instructor, I want to be able to automatically create links in Canvas that directs students to the corresponding JupyterHub / JupyterLab page.
* As a course instructor, I want a way to automatically upload all grades from an nbgrader assignment to Canvas.
* As a course instructor / TA, I want to make sure that nbgrader is running the student’s submission in a sandbox environment, so that if a student writes malicious code, the code will not affect me and other students.
* As a course instructor, I want to be able to assign each TA a separate JupyterHub account, and they can grade the assignment for the same course. It is favorable to record who graded which assignment / submission.
* As a course instructor / TA, I want to be able to work on multiple courses with only one account to the system. Currently I have to have one account for each course I am grading.
* As a non-English speaker / teacher, I hope nbgrader can have a internationalized interface (e.g. Chinese, Japanese) so that it is more friendly to my students. 
* As a teacher, I would like to easily import student roster from Canvas when the quarter begins. And when I notice students add , drop, or switch sections of the course, I would like to have a way to easily manage the change. 
* As a instructor, I would like to have a back button in formgrader (url is /user/<username>/formgrader) of ngshare so that I can easily go back to my JupyterHub homepage after I grade a homework 
* As a instructor / TA, I hope ngshare can have a way to handle regrade requests, instead of having all students email me and looking for each student in the system when handling each regrade request. 
* As a Windows server cluster manager, I hope nbgrader and ngshare can support more platforms by fixing problems like path name translation. 

