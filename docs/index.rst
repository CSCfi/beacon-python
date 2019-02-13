Python-based Beacon API Server
==============================

.. epigraph::

    The Beacon project was launched in 2014 to show the willingness of researchers to enable the secure sharing of
    genomic data from participants of genomic studies.
    Beacons are web-servers that answer questions such as:

    Does your dataset include a genome that has a specific nucleotide (e.g. `G`)
    at a specific genomic coordinate (e.g. `Chr.1 position 111,111`)?

    To which the Beacon must respond with yes or no, without referring to a specific individual.

    -- https://github.com/ga4gh-beacon/specification

``beacon-python`` Web Server implements the `Beacon API 1.0.0+ specification <https://github.com/ga4gh-beacon/specification>`_
by providing an easy to use and configure web application, and also adds support for (e.g. wildcard search) and more.

In order to facilitate loading data, we provide out of the box a ``*.vcf``/``*.vcf.gz`` data loader into
the Beacon :ref:`database`, but an existing database can be utilised as well see :ref:`database-setup`.

Out of the box the ``beacon-python`` offers:

* Beacon API 1.0.1+ specification compliant;
* processing and loading VCF files based on `cyvcf2 <http://brentp.github.io/cyvcf2/>`_ ;
* asynchronous web server;
* OAuth2 JWT token validation, by default for ELIXIR AAI, with retrieving researcher bona fide status;
* Handling `REMS <https://rems2docs.rahtiapp.fi/>`_ permissions for ``CONTROLLED`` datasets,
  additional modules can be added - see :ref:`permissions`;
* 1000 genome dataset loader - see :ref:`genome-dataset` instructions;
* deployment `Docker container <https://hub.docker.com/r/cscfi/beacon-python/>`_.

----

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   Setup Instructions <instructions>
   Database               <db>
   Deployment             <deploy>
   API Examples           <example>
   Handling Permissions   <permissions>
   Python Modules         <code>
   Testing                <testing>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
