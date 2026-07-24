#!/usr/bin/env python3

# elliot-gh/cloudflare-ddns
# Python 3 rewrite of the bash cf-ddns client, using a JSON config.
#
# The config is organized per root domain. Each root domain holds the
# Cloudflare zone identifier and auth token, and any records listed under it
# (including subdomains such as a.example1.com) inherit that zone/auth.

import json
import re
import sys
import urllib.error
import urllib.request

PREFIX = "[cf-ddns]"

# Change this as needed or pass arg
CONFIG_PATH = "/root/.secrets/cf-ddns/cf-ddns.config"

IP_SERVICE = "https://ipv4.icanhazip.com/"
CF_API = "https://api.cloudflare.com/client/v4"

IPV4_RE = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")


def log(message):
    print(f"{PREFIX} {message}")


def err(message):
    print(f"{PREFIX} {message}", file=sys.stderr)


def load_config(path):
    try:
        with open(path, mode="r", encoding="utf-8") as f:
            config = json.load(f)
    except OSError as exc:
        err(f"Could not read config file at {path}: {exc}")
        sys.exit(1)
    except json.JSONDecodeError as exc:
        err(f"Config file at {path} is not valid JSON: {exc}")
        sys.exit(1)

    domains = config.get("domains")
    if not isinstance(domains, dict) or not domains:
        err("Config must contain a non-empty 'domains' object.")
        sys.exit(1)

    for root_domain, settings in domains.items():
        if not isinstance(settings, dict):
            err(f"Config for '{root_domain}' must be an object.")
            sys.exit(1)
        if not settings.get("auth_token"):
            err(f"Config for '{root_domain}' is missing 'auth_token'.")
            sys.exit(1)
        if not settings.get("zone_identifier"):
            err(f"Config for '{root_domain}' is missing 'zone_identifier'.")
            sys.exit(1)
        if not isinstance(settings.get("records"), dict) or not settings["records"]:
            err(f"Config for '{root_domain}' is missing a non-empty 'records' object.")
            sys.exit(1)

    return config


def get_public_ip():
    try:
        with urllib.request.urlopen(IP_SERVICE, timeout=15) as response:
            ip = response.read().decode("utf-8").strip()
    except urllib.error.URLError as exc:
        err(f"Failed to fetch public IP from {IP_SERVICE}: {exc}")
        sys.exit(1)

    log(f"Got IP: {ip}")
    if not IPV4_RE.match(ip):
        err("Didn't get a valid IPv4! Exiting...")
        sys.exit(1)
    return ip


def cf_request(method, url, auth_token, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", f"Bearer {auth_token}")
    request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            return json.load(exc)
        except (json.JSONDecodeError, ValueError):
            return {"success": False, "errors": [{"message": str(exc)}]}
    except urllib.error.URLError as exc:
        return {"success": False, "errors": [{"message": str(exc)}]}


def update_record(record_name, proxied, ip, ttl, zone_identifier, auth_token):
    print(f"\n{PREFIX} ---------- {record_name} ----------")

    log("Getting existing record from Cloudflare")
    lookup = cf_request(
        "GET",
        f"{CF_API}/zones/{zone_identifier}/dns_records?type=A&name={record_name}",
        auth_token,
    )

    if not lookup.get("success") or not lookup.get("result"):
        err(f"Getting existing record failed for {record_name}. DUMPING RESULTS:\n{lookup}")
        return

    record = lookup["result"][0]
    old_ip = record.get("content")
    record_identifier = record.get("id")

    if ip == old_ip:
        log("IP has not changed.")
        return

    log("Overwriting existing DNS record")
    update = cf_request(
        "PUT",
        f"{CF_API}/zones/{zone_identifier}/dns_records/{record_identifier}",
        auth_token,
        {
            "name": record_name,
            "ttl": ttl,
            "type": "A",
            "content": ip,
            "proxied": proxied,
        },
    )

    if update.get("success"):
        log(f"IPv4 content '{ip}' has been synced to Cloudflare.")
    else:
        err(f"Update failed for {record_identifier}. DUMPING RESULTS:\n{update}")


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else CONFIG_PATH

    log("Started")
    log(f"Reading config file at {config_path}")
    config = load_config(config_path)

    default_ttl = config.get("ttl", 1)

    ip = get_public_ip()

    log("Beginning main loop")
    for root_domain, settings in config["domains"].items():
        zone_identifier = settings["zone_identifier"]
        auth_token = settings["auth_token"]
        ttl = settings.get("ttl", default_ttl)

        for record_name, record_settings in settings["records"].items():
            record_settings = record_settings or {}
            proxied = bool(record_settings.get("proxied", False))
            update_record(record_name, proxied, ip, ttl, zone_identifier, auth_token)


if __name__ == "__main__":
    main()
