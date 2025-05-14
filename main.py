import requests as req
import re
from firerequests import FireRequests
import patoolib
import os
import shutil
import tarfile

TOKEN = os.getenv("GITHUB_TOKEN")

os.makedirs('bin', exist_ok=True)

with open('bin/.gitkeep', 'w') as f:
    f.write("#")


def get_release_new(owner: str, repo: str):
    resp = req.get(
        f"https://api.github.com/repos/{owner}/{repo}/releases/latest",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    )

    result = resp.json()
    print(result)
    tag_name, assets = result['tag_name'], result['assets']
    list_latest = []
    for c in assets:
        list_latest.append({'name': c['name'], 'url': c['url']})

    return (tag_name, list_latest)


def cek_file_release(list_assets: list) -> dict:
    for c in list_assets:
        name = c['name']

        if "cloudflared-linux-amd64" == name:
            return c

        if re.search(
            r'(linux-amd64|linux-x86_64|linux_amd64|linux_x86_amd64|x86_64)',
            name,
            re.IGNORECASE
        ):
            if name.endswith('.tar.gz') or\
                name.endswith('.tgz'):
                    return c

def download_file(asset: dict):
     fr = FireRequests()
     fr.download(
        urls=asset['url'],
        chunk_size=2 * 1024 * 1024,
        filenames=asset['name'],
        headers={
            "Accept": "application/octet-stream",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28"
        },
        show_progress=True
     )


def download_all(list_name_repo: dict):
      for x, y in list_name_repo.items():
         tagname, list_assets = get_release_new(x, y)
         cek_download = cek_file_release(list_assets)
         download_file(cek_download)
         name = cek_download['name']
         if re.search(r'cloudflare', name, re.IGNORECASE):
              shutil.move(name, "bin/cloudflared")
              continue

         patoolib.extract_archive(name, outdir="bin")
         os.remove(name)

def create_tar_gz(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def start_download():
     list_repo = {
          "AlistGo": "alist",
          "surrealdb": "surrealdb",
          "caddyserver": "caddy",
          "cloudflare": "cloudflared",
          "antman666": "Aria2-Pro-Core"
     }

     download_all(list_repo)
     os.remove("bin/LICENSE")
     os.remove("bin/README.md")
     create_tar_gz("bin.tar.gz", "bin")



start_download()