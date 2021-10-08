.. CanDIG Federation documentation master file, created by
   sphinx-quickstart on Wed Feb  5 14:13:15 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to CanDIG Federation's documentation!
=============================================


The Federation service is a one of the services which make up the CanDIG v2 platform. It acts as an entry
point for all incoming requests made to CanDIG, passing it along to the specified service, federating the request among the
nodes in the CanDIG network and aggregating all the responses.

It is based off CanDIG's `Python Model Service`__, an OpenAPI stack utilizing Connexion, SQLAlchemy, Bravado-core,
Pytest and Travis-CI.





.. __: https://github.com/CanDIG/python_model_service



.. toctree::
   :maxdepth: 4

   install
   run

   modules
   examples
   testing




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
