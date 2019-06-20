#!/bin/bash

cd package
zip -r9 ../function.zip .
cd ..
zip -g function.zip lambda.py