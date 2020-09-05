# Cloudflare DDNS bash client with systemd

From <https://gist.github.com/radiantly/3dbff163624ca3dd32ee8ecf225a7b02>, updated with minor changes:

- Handle multiple records, with setting proxied setting for each.
- Quick IPv4 validation
- Minor update to Cloudflare handling
- Rename from cfupdater to cf-ddns
- Service waits for `network-online.target`
- Timer example is 15 minutes

___

This is a bash script to act as a Cloudflare DDNS client, useful replacement for ddclient.

## How to use

1) Put the `cf-ddns` file to `/usr/local/bin`
2) `chmod +x /usr/local/bin/cf-ddns`
3) Create a systemd service unit at `/etc/systemd/system/`, the `cf-ddns.service` is shown as an example.
4) Create a systemd timer unit at **the same location of the service unit**. The `cf-ddns.timer` is shown as an example.
5) `sudo systemctl enable cf-ddns.timer`
6) `sudo systemctl start cf-ddns.timer`

## Note

An advantage of using this script over others is that this one supports usage of Cloudflare API tokens.
The default `cf-ddns.timer` is set to execute the script **every 15 minutes**.
