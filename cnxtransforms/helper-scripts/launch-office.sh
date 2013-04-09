#!/bin/sh
# Should be run as user www-data, perhaps as so:
# sudo su www-data ./oolaunch
cd /tmp
echo "localhost" >xvfb.auth.$$
Xvfb -auth /tmp/xvfb.auth.$$ :1 -screen 0 1024x768x24 &

# 'swriter' is the commandline to the star office (and derivatives)
#   writer application.
SWRITER=$(which swriter)
SWRITER=${SWRITER:-$(which lowriter)}
echo $SWRITER

$SWRITER --headless "--accept=socket,host=localhost,port=2002;urp;" -display :1.0 &
