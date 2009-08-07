#!/bin/bash
# tu nombre de usuario tiene que existir como superusuario de postgresq

echo "Dropping database"
dropdb merengue
echo "Creating database"
createdb -T template_postgis --owner=merengue merengue

if (( $? )) ; then
  echo "Unable to create database (check django or shell are not running and try again)."
  exit 1
fi
./manage.py syncdb --noinput
./manage.py migrate
echo "Enter password for 'admin' user:"
./manage.py createsuperuser --username=admin --email=dev@merengueproject.com

if (( $? )) ; then
  echo "Unable to create the new schemaNo (syncdb). "
  exit 1
fi
