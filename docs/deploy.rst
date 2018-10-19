Deployment
==========

The recommended means of deployment for the Python based Beacon Web Server is via
docker engine.
In this section we illustrate some means of building and running the application.

Dockerfile
----------

Using vanilla docker in order to build the image:

.. code-block:: console

    $ git clone https://github.com/CSCfi/beacon-python
    $ cd beacon-python
    $ docker build -t cscfi/beacon-python


Source to Image
---------------

Using OpenShift's ``s2i`` means of building the Docker image requires
`source2image <https://github.com/openshift/source-to-image>`_ installed.

.. code-block:: console

    $ git clone https://github.com/CSCfi/beacon-python
    $ cd beacon-python
    $ s2i build . centos/python-36-centos7 cscfi/beacon-python

After the image has been built one can use it with the simple Docker ``run``
or as part of a docker-compose file or as illustrated below with Kubernetes.

.. code-block:: console

    $ docker run -p 5050:5050 cscfi/beacon-python

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
                  name: browsepy
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
