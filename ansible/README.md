# How to install on a target system using Ansible

## Deploy to Raspberry from Raspperry itself
First ssh to the Pi and sync the git repo to it. After that you can just run `./run.sh` from within the ansible folder.
## Deploy to Raspberry from Linux machine
`ansible-playbook site.yml --inventory="192.168.1.8," -u pi -k`
