#!/bin/bash
SENDER="main.py robust.py simple.py app.py_sender"
RECEIVER="main.py robust.py simple.py app.py_receiver micropyGPS.py sdcard.py just_mount.py"

SOURCE="master"

for NODE in `ls | grep ^node`; do
 echo "rm -rf `pwd`/${NODE}/*"
 rm -rf `pwd`/${NODE}/*

 if [[ ${NODE} =~ ^node0[6-9]$ ]]; then
  DATASOURCE=${SENDER}
 else
  DATASOURCE=${RECEIVER}
 fi

 for SFILE in `echo ${DATASOURCE}`; do
  DFILE=${SFILE}
  if [ ${SFILE} == "app.py_sender" ]; then
   DFILE="app.py"
  fi
  if [ ${SFILE} == "app.py_receiver" ]; then
   DFILE="app.py"
  fi
  echo " cp ${SOURCE}/${SFILE} ${NODE}/${DFILE}"
  cp ${SOURCE}/${SFILE} ${NODE}/${DFILE}
  echo ${DFILE} >> ${NODE}/manifest.txt
  echo "`date +%Y%m%d%H%M%S`" > ${NODE}/version.txt
 done
done
