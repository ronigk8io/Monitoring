#!/bin/bash

timeout 5 wget -qO- "https://horizon.stellar.org/ledgers?limit=1&order=desc" --no-check-certificate 2>/dev/null | jq -r "._embedded.records[0].sequence"


