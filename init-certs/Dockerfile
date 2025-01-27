FROM alpine:latest

RUN apk add --no-cache openssl

WORKDIR /app

COPY generate-certs.sh .
RUN chmod +x generate-certs.sh

CMD ["./generate-certs.sh"]
