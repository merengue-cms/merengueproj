#!/bin/bash

# Constants
DISPLAY=":0"
JAVA=/usr/bin/java

if [ `/bin/hostname` = "vostro200-2" ]
then
   SELENIUM=/usr/local/src/selenium-remote-control-1.0-beta-2/selenium-server-1.0-beta-2/selenium-server.jar
else
   SELENIUM=/usr/local/src/selenium-remote-control-1.0.1/selenium-server-1.0.1/selenium-server.jar
fi

# Arguments
SELENIUM_DIR=$1
shift

HOST=$1
shift

export DISPLAY

OUTPUT=0
while [ "$1" != "" ]; do
    SUITE=$1
    LOGFILE=$SELENIUM_DIR/$SUITE/selenium.log
    RESULTFILE=$SELENIUM_DIR/$SUITE/output.html

    $JAVA -jar $SELENIUM -htmlSuite "*chrome" $HOST $SELENIUM_DIR/$SUITE/suite.html $RESULTFILE -log $LOGFILE -timeout 3600 -port 4555
    grep "<td>numTestFailures:</td>" $RESULTFILE -A 1 | grep "<td>0</td>"
    OUTPUT=$(($OUTPUT + $?))

    chmod a+rx $SELENIUM_DIR/$SUITE/
    chmod a+r $RESULTFILE
    chmod a+r $LOGFILE

    echo "You can see the output at this location:"
    echo "http://buildbot.yaco.es/resultados-selenium/merengue/$SUITE/output.html"
    echo "http://buildbot.yaco.es/resultados-selenium/merengue/$SUITE/selenium.log"

    shift
done

chmod a+rx .
chmod a+rx ..
chmod a+rx ../..
chmod a+rx ../../..

exit $OUTPUT

