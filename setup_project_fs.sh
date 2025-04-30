#!/bin/bash

PROJECT_NAME="mini-nginx"
mkdir -p $PROJECT_NAME/{core,static,logs}
cd $PROJECT_NAME

# Create basic files
touch config.yaml requirements.txt main.py
touch core/{__init__.py,server.py,helper.py,router.py,proxy.py,logger.py}
touch static/index.html
touch logs/access.log


echo "✅ Project structure created in '$PROJECT_NAME'"
