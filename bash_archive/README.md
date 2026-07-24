# Cloudflare DDNS bash client with systemd

From <https://gist.github.com/radiantly/3dbff163624ca3dd32ee8ecf225a7b02>, updated with minor changes:

- Seperate config file.
- Handle multiple records with proxied setting for each.
- Added TTL option.
- Minor validation improvements.
- Rename from cfupdater to cf-ddns
- Service waits for `network-online.target`
- Timer example is 15 minutes

___

This is a bash script to act as a Cloudflare DDNS client, useful replacement for ddclient.

## How to use

1) Put the `cf-ddns` file in `/usr/local/bin`
2) `chmod +x /usr/local/bin/cf-ddns`
3) Put the `cf-ddns.config` in a safe folder, such as "/root/.secrets/cf-ddns/cf-ddns.config" with permissions such as `500`. Make sure to update the script config path!
4) Create a systemd service unit at `/etc/systemd/system/`. `cf-ddns.service` is shown as an example.
5) Create a systemd timer unit at **the same location of the service unit**. `cf-ddns.timer` is shown as an example.
6) `sudo systemctl enable cf-ddns.timer`
7) `sudo systemctl start cf-ddns.timer`

## Note

An advantage of using this script over others is that this one supports usage of Cloudflare API tokens.
The default `cf-ddns.timer` is set to execute the script every 15 minutes, starting 5 minutes after boot.
