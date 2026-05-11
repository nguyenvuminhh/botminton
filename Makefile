connect:
	ssh -i "~/.ssh/Botminton-Key.pem" ubuntu@ec2-13-60-32-167.eu-north-1.compute.amazonaws.com

redeploy:
	docker rm -f botminton && \
	docker build -t botminton . && \
	docker run -d \
	  --name botminton \
	  --restart unless-stopped \
	  --env-file .env \
	  -p 127.0.0.1:8000:8000 \
	  botminton
