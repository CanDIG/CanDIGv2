.. _contribution:

**********************
Contribution Guideline
**********************

.. warning::

    This guide is a work in progress, and is incomplete.


If you encounter a bug, or have a problem of using the service, please contact us by opening an issue at https://github.com/CanDIG/candig_cnv_service.

++++++++++++++++
GitHub workflow
++++++++++++++++

We mainly employ three different types of branches: feature branches, develop branch, and
master branch.

Feature branches are used to resolve a limited set of issues, and typically
follows the naming convention of ``username/fix_one_particular_issue``. When initiating a
PR, you should request it to be merged back into the ``develop`` branch. The commits in
individual feature branches are usually squashed, and code review usually happens at this step.

Develop branch is used to host code that has passed all the tests, but may not yet be production-ready,
As a developer, you are welcome to play with this branch to test some of the new functionalities.

If you would like to contribute code, please fork the package to your own git repository,
then initiate a PR to be merged into develop.
