$SERVER = "myserver"
$REMOTE_PATH = "/var/www/phillongworth-site/html"

# This line uses the variables above
scp -r ./* "${SERVER}:${REMOTE_PATH}"