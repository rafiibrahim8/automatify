#!/bin/bash

# https://stackoverflow.com/questions/22080937/skip-blank-lines-when-iterating-through-file-line-by-line
for line in `sed '/^$/d' .env`; do
    e_vars="$e_vars -e $line"
done
~/.local/bin/gunicorn -b 127.0.0.1:65003 wsgi:app $e_vars

