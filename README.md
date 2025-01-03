# KSONG: Karaoke Software Optimized for Networking and Party Games

## Architecture

![](ksong-arch.png) 

## Usage

```bash
pip install -r requirements.txt
python server/main.py 5001 /path/to/db /path/to/music "http://127.0.0.1:5000" &
hypercorn audio_server/signaling:app --bind 0.0.0.0:5000
```

Replace `/path/to/db` with the path to your database. If no database file exists at that location, a new one will be created. Also, replace `/path/to/music` with the directory where you store your music.

## Deployment

If you are deploying within a local network, you also need to configure HTTPS. Test certificates are provided under the ssl/ path.

**WARNING**: Please do not use this certificate in a production environment; it is for testing purposes only.

e.g.

```bash
python server/main.py 5001 "/home/samuel/Projects/KSong/db/song.db" "/media/samuel/Samsung USB/Music" "https://192.168.3.99:5000" --certfile ssl/cert.pem --keyfile ssl/key.pem
hypercorn audio_server/signaling:app --bind 0.0.0.0:5000 --certfile ssl/cert.pem --keyfile ssl/key.pem  --certfile ssl/cert.pem --keyfile ssl/key.pem
```

Here, `"/home/samuel/Projects/KSong/db/song.db"` is the path to the database file, `"/media/samuel/Samsung USB/Music"` is the path for searching the music library, and `"https://192.168.3.99:5000"` is the address of your machine on the local network. You need to change these three settings to your own. Additionally, in actual deployment, you will also need to replace the `certfile` and `keyfile`.