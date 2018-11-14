all:

clean:
	docker rm -v $(docker ps -aq)
	sudo rm -rf $DIR/etc minio_access_key minio_secret_key

minio-server:

minio-secrets:
	if [ ! -f minio_access_key ]; then echo admin > minio_access_key; fi
	if [ ! -f minio_secret_key ]; then
		KEY=$(dd if=/dev/urandom bs=1 count=16 2>/dev/null | base64 | rev | cut -b 2- | rev)
		echo $KEY > minio_secret_key
	fi
	access_key=$(cat minio_access_key)
	secret_key=$(cat minio_secret_key)

mc-shell: minio-secrets
	docker run -it --name=mc_shell --entrypoint=/bin/sh -e MINIO_ACCESS_KEY=$access_key -e MINIO_SECRET_KEY=$secret_key minio/mc

docker-net:
	docker network create --driver overlay --attachable traefik_net

docker-volumes:
	docker volume create minio-config
	docker volume create minio-data

traefik:
	docker stack deploy --compose-file $DIR/lib/traefik/traefik-net.yml traefik_net

