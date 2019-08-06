Deployment
==========

The recommended means of deployment for a production web server of Beacon-python is via
a container image (e.g. Docker image).
In this section we illustrate several means of building and running a
``beacon-python`` application via a Docker container image.

Dockerfile
----------

Using vanilla docker in order to build the image - the tag can be customised:

.. code-block:: console

    $ git clone https://github.com/CSCfi/beacon-python
    $ docker build -t cscfi/beacon-python .
    $ docker run -p 5050:5050 cscfi/beacon-python

.. _s2i-build:

Source to Image
---------------

Using OpenShift's ``s2i`` means of building the Docker image requires
`source2image <https://github.com/openshift/source-to-image>`_ installed.

.. code-block:: console

    $ git clone https://github.com/CSCfi/beacon-python
    $ cd beacon-python
    $ s2i build . centos/python-36-centos7 cscfi/beacon-python

After the image has been built, one can use it with the simple Docker ``run``
(requires connection to a DB in the same Docker network)
or as part of a docker-compose file or as illustrated below with Kubernetes.

.. code-block:: console

    $ docker run -p 5050:5050 cscfi/beacon-python


Docker Compose
--------------

.. code-block:: console

    $ git clone https://github.com/CSCfi/beacon-python
    $ cd beacon-python/deploy
    $ docker build -t cscfi/beacon-python .
    $ docker-compose up -d


Kubernetes Integration
----------------------

For use with Kubernetes we provide ``YAML`` configuration.

.. code-block:: yaml

    apiVersion: apps/v1
    kind: Deployment
    metadata:
      labels:
        role: beacon
      name: beaconpy
      namespace: beacon
    spec:
      selector:
        matchLabels:
          app: beaconpy
      template:
        metadata:
          labels:
            app: beaconpy
            role: beacon
        spec:
          containers:
            - image: cscfi/beacon
              imagePullPolicy: Always
              name: beacon
              ports:
                - containerPort: 5050
                  name: beaconpy
                  protocol: TCP
              volumeMounts:
                - mountPath: /files
                  name: data
          volumes:
            - name: data
              persistentVolumeClaim:
                claimName: beaconpy
    ---
    apiVersion: v1
    kind: Service
    metadata:
      name: beacon
      labels:
        app: beaconpy
    spec:
      type: NodePort
      ports:
        - port: 5050
          targetPort: 5050
          protocol: TCP
          name: web
      selector:
        app: beaconpy

.. _genome-dataset:

1000 Genome Loader
------------------

.. note:: We use data from: `1000 Genome FTP <ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/>`_.

For use with loading the whole 1000 genome dataset we provide a docker image ``cscfi/beacon-dataloader``
that downloads the whole 1000 genome ``vcf.gz`` files (>18GB disk space) and a ``YAML`` configuration
for Kubernetes illustrated below.

The container uses the same Environment Variables specified at: :ref:`env-setup` and adds two more:

+---------------------+-----------------------------------+--------------------------------------------------+
| ENV                 | Default                           | Description                                      |
+---------------------+-----------------------------------+--------------------------------------------------+
| `FTP_URL`           | `ftp://ftp.1000genomes.ebi.ac.uk` | The URL for the FTP server.                      |
+---------------------+-----------------------------------+--------------------------------------------------+
| `FTP_DIR`           | `/vol1/ftp/release/20130502/`     | Name of the directory.                           |
+---------------------+-----------------------------------+--------------------------------------------------+

.. code-block:: yaml

        apiVersion: batch/v1
        kind: Job
        metadata:
          name: dataloader
        spec:
          template:
            metadata:
              name: dataloader
            spec:
              containers:
              - name: dataloader
                image: cscfi/beacon-dataloader
                env:
                - name: TABLES_SCHEMA
                  value: /app/init.sql
                - name: DATABASE_URL
                  valueFrom:
                    secretKeyRef:
                      key: uri
                      name:
                - name: DATABASE_NAME
                  valueFrom:
                     secretKeyRef:
                        key: database_name
                        name:
                - name: DATABASE_USER
                  valueFrom:
                    secretKeyRef:
                      key: username
                      name:
                - name: DATABASE_PASSWORD
                  valueFrom:
                    secretKeyRef:
                      key: password
                      name:
                volumeMounts:
                - name: data
                  mountPath: /app/data
              restartPolicy: Never
              imagePullPolicy: Always
              volumes:
              - name: data
                persistentVolumeClaim:
                  claimName: 1000genome
