@echo off
    
SET PYTHONPATH=src

:: CALL pipreqs --use-local --force --encoding utf8 --savepath requirements.txt src
RMDIR /Q /S nonemptydir docs\_apidoc
CALL sphinx-apidoc -H "Code" -o docs/_apidoc src
CALL python setup.py build_sphinx
CALL python setup.py test

PAUSE
