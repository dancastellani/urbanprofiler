export URBAN_PROFILER_ENVORINMENT='STAGING'
export SERVER_IP=100.67.54.124

#New Relic
NEW_RELIC_APP_NAME='Urban Profiler (Staging)'
export NEW_RELIC_CONFIG_FILE='/files/projects/auto-etl/data-finder-site/newrelic.ini'
export NEW_RELIC_ENVIRONMENT='staging'

# export NEW_RELIC_CONFIG_FILE=newrelic.ini 
# export NEW_RELIC_ENVIRONMENT=development 

./run-server.sh
