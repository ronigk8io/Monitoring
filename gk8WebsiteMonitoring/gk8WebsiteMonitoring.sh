#!/bin/bash

# Vars.   Notice: data dir contains strings and web url and page
WEB_PAGE="$(cat data/WEB_PAGE)"
WEB_URL="$(cat data/WEB_URL)/"$WEB_PAGE

MISSING_STRINGS_FILE="missing-strings.txt"
MISSING_STRINGS_OUTPUT_FILE="missing-strings-output-file.txt"
MISSING_FILES_LIST_FILE="missing-files.txt"

EMAIL_SCRIPT="sendEmailWithAmazonSes_forWebsiteMonitoring.sh"
#EMAIL_SCRIPT="sendEmailWithAmazonSes_forWebsiteMonitoring_test.sh"

# Created working files
CREATED_FILES="index.html* $WEB_PAGE* wget-log* $MISSING_STRINGS_FILE $MISSING_STRINGS_OUTPUT_FILE $MISSING_FILES_LIST_FILE"

# Pre clean
rm -f $CREATED_FILES && echo "Pre cleaned."

# make phone call
make_phone_call () {
  python2 ../phoneCall/caller_python2.py
}

# Post clean
post_clean () {
rm -f $CREATED_FILES && echo "Post cleaned."
}

# Check strings files are present
MISSING_FILES=""
for i in 1 2 3 4 ; do
  if [[ ! -f data/STRING_$i ]] ; then
    MISSING_FILES+="STRING_$i "
    echo $MISSING_FILES > $MISSING_FILES_LIST_FILE
  fi
done
[[ -s $MISSING_FILES_LIST_FILE ]] && echo "Missing files: " && cat $MISSING_FILES_LIST_FILE

if [[ -f $MISSING_FILES_LIST_FILE ]] ; then
  bash $EMAIL_SCRIPT \
  "Cannot check Web URL: $WEB_URL - missing strings files on monitoring server" \
  "Missing strings files on monitoring server: $(cat $MISSING_FILES_LIST_FILE)"
  make_phone_call
  echo "Exiting."
  post_clean
  exit
fi

# Download webpage
timeout 30 wget "$WEB_URL" 2>/dev/null && echo "Downloaded webpage..."

# Check webpage
if [[ -f $WEB_PAGE ]] ; then
  echo "Webpage found."

  # Check if all 1-4 strings found in webpage
  for i in 1 2 3 4 ; do
    grep -i "$(cat data/STRING_$i)" $WEB_PAGE &>/dev/null || echo STRING_$i | tee -a $MISSING_STRINGS_FILE
  done

  # Check if there were missing strings
  if [[ ! -f $MISSING_STRINGS_FILE ]] ; then
    echo "GK8 Website health check passed!"
  else
    echo "Could not find at least 1 of the desired strings: $(cat $MISSING_STRINGS_FILE)"

    # Create missing string output file
    for i in $(cat $MISSING_STRINGS_FILE) ; do
      echo $i":" $(cat data/$i) ";" | tee -a $MISSING_STRINGS_OUTPUT_FILE
    done

    bash $EMAIL_SCRIPT \
      "Some error in strings grep from Web URL: $WEB_URL" \
      "Tried unsuccessfully to grep these strings from this Web URL $WEB_URL: $(cat $MISSING_STRINGS_OUTPUT_FILE)"
    make_phone_call
  fi

else
  echo "Could not find webpage!"
  bash $EMAIL_SCRIPT "Some error in wget." "Tried to wget website, but $WEB_PAGE was not created. Is the URL alive?"
  make_phone_call
fi

post_clean

