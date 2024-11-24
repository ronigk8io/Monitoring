aws ses send-email \
    --from monitoring_no_reply@gk8.io \
    --to noam@gk8.io support@gk8.io roni@gk8.io \
    --text "This is for those who cannot read HTML." \
    --text "$2" \
    --html "<h1>SES Monitoring script: Some client nodes are not synced</h1><p>$2</p>" \
    --subject "$1"

