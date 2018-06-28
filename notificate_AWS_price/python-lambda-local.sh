#!/usr/bin/env bash

echo “post masa-billing”
/users/masaakihamada/PycharmProjects/7dtd/venv/bin/python-lambda-local -t 60 -f $1 $2 $3

