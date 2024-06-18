#!/bin/bash
if [[ -e ".venv" ]]
then
    if [[ "$VIRTUAL_ENV" != "" ]]
    then
        echo 'Installing spacy module and eng model'
        pip install numpy==1.26.4 spacy
        python -m spacy download en_core_web_sm
    else
        echo 'Activate the venv'
    fi
else
    echo 'create a new .venv and activate it'
fi