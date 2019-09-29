#!/bin/bash
sudo apt update -y
sudo apt install python3-pip -y
sudo apt-get install nginx -y
sudo apt-get install git-core -y
sudo apt-get install gunicorn3 -y
sudo cat <<EOF > ~/.ssh/gitrepo
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA+4e8nhZxiRTCw8xqEbtz97RkRQjYkgH1CeQYZ1Zx9E+HtI3/
4Rh9wwzIu7XsfkohQL19QwSD8lbd+veSf4LakbnNpTaQO8nrfElVBcEQUioYuB88
+Gb14BeNO3ToLI4OQlHIYi8TQOhuDP4TVJxTOQkcSVCQN7pSCv+vvT1PKc/FILVB
ntMaabYhNXQ5TZZVN0m3i0i5uKNRZcrRmZi8gVh1MBPxqydaBgcbzuCTl7M4iRLM
kqgouVjXfMNCpJe5C3VaLKyn+dQMOnWn+tHTgP6xb4+Q437vS/LoGBDEoKJaQ//V
1ve4L/1CWAhpvvwB5jNXNrJXKLsN+OIY7gSv9wIDAQABAoIBAEtU/9ypBB/2I87Y
bfwZlEXftRgn6hTwmR75PYXVkhOFrjMZREV6PFAqiAQQHGBGe2cUWWu08n+mHJ2J
gErIOgXjDAArM090zh5PKDOs+uJg0T5zvKL40zLmWtovzUlq0kJyk/0z9CRAeJVT
kx6IIzS10c7zXf4Sw3ef1FZtAkSW6Ybr+GAfBT6/Y8t/EZYNzKN5Yl5mKHal9miC
xGAyA0xaDNiZu813fP+npkzxnQHZ651sHXKDb7b/SCG0XaJiWzoddu+A4QK0vjUM
o+BzvlW5Mk7EdBEfbTEfGZM1FnLguxXX6XFiNqC9wGVbKYbzxczpiuwmBeFs467T
ltFpsoECgYEA/xd6rW/icTDjHYedA2ePXgxqNZzoKbKBuIzoLzaIfPIwAF+tYPyB
NJeiq6wPRUMFwipijucprx60g/INLmncjoCPX/gyKPvhrRw6PC6T/d+zBryHinJE
NssmS70oFXbR40/rvqDV/bs03XI3/VcGgfHjEUcuHfVJ1GMCwz04/FECgYEA/G0C
3rvO1jjQ5PcaSZqzgozSmPDtOo7xRgVEVn4b1jJG9dlXHhMIt0+NGvx5N4oP1inK
jKx5R/VTvAa2trRJx2moJEs6Kc2dN7TCN5z66m1JrxUGAXcu88Lyjj0wcvWM4OC8
gYSMXUslWM5KhEXFO3914+Krleo2DJ5IBOr1fccCgYB9qPdJ0L/fupFmzpNORgmd
7sezOWQ0hjbYzrDh8R8zTarPxFIIYNrVKY18u/mZyPZhO7fpZX5nQdzy0p4jqwp3
OGVohT9QaSQ2vp0BYICOo0/xlZW/YaKwy0pGLRw91pZ2P7yF330KzNmx7L4gEmqm
QJ32uPXC1D5WXZ/Sxan4wQKBgQDWjHUvCWQRMnNi2SAvxVykLrtlIQoRhqNOB3YB
KejREyS7G4LvXfA/lk7xy/vfl+pD9nthO8tNvRfxraco/W3kH0q5pnMGSuxBB9M3
36ZpEIDbXjwfjMSMjXsKKLoAS/L0xC+UyitftFpG8/fkG0U7f+eczPFYV5ye9v1x
qJ8FywKBgQDs4UIo3rvvxAaoqUB5t4kaAJ0NfDdD2lfr3ZfnhRU55ENLiqfYAR9P
V/dLoGJ7wCRbfqEuTBOBMgXLjrFqLVNE6jO3qzF5kZR3uWr5my9TQKUmXJoelZRw
62rPkyFpLrx29mr+5tf/4s+3SJldtJJNOPf9Jb6+YLwGXwLg/betOQ==
-----END RSA PRIVATE KEY-----
EOF
sudo ssh-agent bash -c 'ssh-add ~/.ssh/gitrepo; git clone git@bitbucket.org:ssml-project/ssml-console.git'
pip3 install -r ~/ssml-console/requirements.txt
sudo cat <<EOF > /etc/systemd/system/gunicorn3.service
[Unit]
Description=Gunicorn service
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/ssml-console/src/
ExecStart=/usr/bin/gunicorn3 --workers 3 --bind unix:ssml.sock -m 007 app:app
EOF
sudo systemctl daemon-reload
sudo service gunicorn3 restart
sudo cat <<EOF > /etc/nginx/sites-enabled/ssml
server {
    listen 80;
    server_name console.ssml.com.br;

    location / {
        proxy_pass http://unix:/home/ubuntu/ssml-console/src/ssml.sock;
    }

}
EOF
sudo service nginx restart