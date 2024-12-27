/home/illusionary/.local/bin/hypercorn K_song/signaling:app  --certfile SSL/cert.pem --keyfile SSL/key.pem --bind 0.0.0.0:9002 &
sleep 1
/home/illusionary/.local/bin/hypercorn K_song/ref_backend:app  --certfile SSL/cert.pem --keyfile SSL/key.pem --bind 0.0.0.0:9003 &
