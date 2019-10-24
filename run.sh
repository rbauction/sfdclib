[ -z "$APP_MODE" ] && APP_MODE="test"

sed -i'.old' 's/username:/username: '$(echo $ARTIFACTORY_USER)'/g' /root/.pypirc
sed -i'.old' 's/password:/password: '$(echo $ARTIFACTORY_PASSWORD)'/g' /root/.pypirc
sed -i'.old' 's/\%40/\@/g' /root/.pypirc

if [ $APP_MODE = "deploy" ]; then
  cat /root/.pypirc
  python setup.py sdist upload -r artifactory
fi
