# Cloudflare DDNS client (Python 3) with systemd

A Cloudflare DDNS client, Originally a bash script (see `bash_archive/`), now rewritten in Python 3 using a JSON config.

___

## Configuration

The config is a single JSON file. Copy the provided `cf-ddns.config.example.json` to `cf-ddns.config.json` (dropping the `.example`) and edit as appropriate.

By default the script reads the config from `/root/.secrets/cf-ddns/cf-ddns.config.json` (change `CONFIG_PATH` at the top of `cf-ddns.py`, or pass a path as the first argument).

```json
{
  "ttl": 1,
  "domains": {
    "example1.com": {
      "auth_token": "auth_token_here",
      "zone_identifier": "zone_id_here",
      "records": {
        "example1.com": { "proxied": false },
        "a.example1.com": { "proxied": true }
      }
    },
    "example2.com": {
      "auth_token": "another_auth_token_here",
      "zone_identifier": "another_zone_id_here",
      "records": {
        "example2.com": { "proxied": false }
      }
    }
  }
}
```

- `auth_token`: Generate an API token at <https://dash.cloudflare.com/profile/api-tokens> with the `dns_records:edit` permission.
- `zone_identifier`: Found in the "Overview" tab of your domain.
- `ttl`: TTL for the DNS record. `1` is automatic; `120` is the Cloudflare minimum.
- `proxied`: `true`/`false` per record.

Records under a root domain share that domain's `zone_identifier` and `auth_token`.

## How to use

1) Put `cf-ddns.py` in `/usr/local/bin`.
2) `chmod +x /usr/local/bin/cf-ddns.py`
3) Copy `cf-ddns.config.example.json` to `cf-ddns.config.json` and put it in a safe folder, such as `/root/.secrets/cf-ddns/cf-ddns.config.json`, with permissions such as `500`. Make sure `CONFIG_PATH` in the script matches, or pass the path as an argument.
4) Create a systemd service unit at `/etc/systemd/system/`. `cf-ddns.service` is shown as an example (update `ExecStart` to point at the Python script).
5) Create a systemd timer unit at the same location of the service unit. `cf-ddns.timer` is shown as an example.
6) `sudo systemctl enable cf-ddns.timer`
7) `sudo systemctl start cf-ddns.timer`

You can also run it manually: `python3 cf-ddns.py` (or `python3 cf-ddns.py /path/to/cf-ddns.config.json`).

## Note

The default `cf-ddns.timer` is set to execute the script every 15 minutes, starting 5 minutes after boot.
