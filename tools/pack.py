#!/usr/bin/env python3
"""Asset-paketin buildaus ja julkaisu.

  tools/pack.py build   --name N --version V --src DIR [--license L] [--upstream URL]
  tools/pack.py publish --name N --version V --notes "..."

build   : zip (<n>-<v>.zip), sha256-tiedosto, PACK.json zipin sisään, manifesti-JSON stdoutiin
publish : gh release create <n>@<v> (repo: mehustamo/dungeon-rush-assets)

Zipin rakenne on aina <name>/... ja suhteelliset polut säilyvät, koska glb-mallien
tekstuuriviittaukset (esim. Textures/colormap.png) ovat suhteellisia.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from datetime import datetime, timezone

REPO = "mehustamo/dungeon-rush-assets"
OUT = "dist"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build(args: argparse.Namespace) -> int:
    src = os.path.abspath(args.src)
    if not os.path.isdir(src):
        print(f"virhe: lähdekansio puuttuu: {src}", file=sys.stderr)
        return 2
    os.makedirs(OUT, exist_ok=True)
    zip_path = os.path.join(OUT, f"{args.name}-{args.version}.zip")

    pack_meta = {
        "name": args.name,
        "version": args.version,
        "license": args.license,
        "upstream": args.upstream,
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(src):
            dirs.sort()
            for f in sorted(files):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, src)
                z.write(full, os.path.join(args.name, rel))
        z.writestr(os.path.join(args.name, "PACK.json"),
                   json.dumps(pack_meta, indent=2, ensure_ascii=False) + "\n")

    digest = sha256_file(zip_path)
    with open(zip_path + ".sha256", "w") as f:
        f.write(f"{digest}  {os.path.basename(zip_path)}\n")

    url = f"https://github.com/{REPO}/releases/download/{args.name}%40{args.version}/{os.path.basename(zip_path)}"
    entry = {
        "name": args.name,
        "version": args.version,
        "url": url,
        "sha256": digest,
        "dest": f"assets/vendor/{args.name}",
        "license": args.license,
        "upstream": args.upstream,
    }
    print(json.dumps(entry, indent=2, ensure_ascii=False))
    print(f"\nzip: {zip_path} ({os.path.getsize(zip_path)} B)", file=sys.stderr)
    return 0


def publish(args: argparse.Namespace) -> int:
    zip_path = os.path.join(OUT, f"{args.name}-{args.version}.zip")
    sha_path = zip_path + ".sha256"
    for p in (zip_path, sha_path):
        if not os.path.exists(p):
            print(f"virhe: {p} puuttuu — aja ensin build", file=sys.stderr)
            return 2
    tag = f"{args.name}@{args.version}"
    cmd = ["gh", "release", "create", tag, zip_path, sha_path, "--repo", REPO,
           "--title", f"{args.name} {args.version}", "--notes", args.notes or zip_path]
    print("+ " + " ".join(cmd), file=sys.stderr)
    return subprocess.call(cmd)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("build", "publish"):
        p = sub.add_parser(name)
        p.add_argument("--name", required=True)
        p.add_argument("--version", required=True)
        p.add_argument("--src", default=".")
        p.add_argument("--license", default="CC0-1.0")
        p.add_argument("--upstream", default="")
        p.add_argument("--notes", default="")
    args = ap.parse_args()
    return build(args) if args.cmd == "build" else publish(args)


if __name__ == "__main__":
    raise SystemExit(main())
