# SSL Certificates Placeholder
# Replace with your actual SSL certificates

# For Let's Encrypt:
# 1. Install certbot: sudo apt install certbot
# 2. Get certificate: sudo certbot certonly --nginx -d search.sridharhomelab.in
# 3. Copy certs:
#    cp /etc/letsencrypt/live/search.sridharhomelab.in/fullchain.pem cert.pem
#    cp /etc/letsencrypt/live/search.sridharhomelab.in/privkey.pem key.pem

# For self-signed (development only):
# openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=search.sridharhomelab.in"