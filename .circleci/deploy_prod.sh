#!/bin/bash

echo "`date` Start circleci deploy"
ssh -o StrictHostKeyChecking=no $DEPLOY_USER@$DEPLOY_SERVER "$DEPLOY_SCRIPT"
