hypercorn K_song/signaling:app  --certfile SSL/cert.pem --keyfile SSL/key.pem --bind 0.0.0.0:9000 &
sleep 1
hypercorn K_song/ref_backend:app  --certfile SSL/cert.pem --keyfile SSL/key.pem --bind 0.0.0.0:5000 &
