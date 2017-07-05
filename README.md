# janeway-fab
Fabric commands for Janeway. The commands will allow you to remotely control some of janeway's functions including updating the codebase, migrating and collecting static assets.

## Getting Started
Initially you will need to do the following:

1. Make sure your public key is registered with the server.
2. Install fabric (sudo apt-get install fabric on Deb, or pip install -e git+https://github.com/fabric/fabric/#egg=fabric)
3. Update fab_settings.py with your servers details
4. Note that these scripts assume you are using a virtualenv (if you aren't, you 100% should)
5. Start executing scripts!

## Executing a script

Fabric scripts look like the following example

```fab server janeway.backup```
