#!/bin/bash

ANSIBLE_CONFIG=site.cfg ansible-playbook site.yml --ask-become-pass $@
