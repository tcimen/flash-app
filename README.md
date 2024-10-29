# flash-app
apt-get update && apt-get install -y postgresql-client
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB

# BUILT
docker build -t 1991199119911991sassd/flask-app:latest .
docker push 1991199119911991sassd/flask-app:latest
kubectl rollout restart deployment flask-app -n my-flask-app