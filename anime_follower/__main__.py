import qbittorrentapi
import typer
from typing import Optional
from rich import print
from rich.pretty import pprint
import requests

app = typer.Typer()

@app.command()
def add(ctx: typer.Context,
        name: str,
        category: str = typer.Option("Anime", "--category", "-c"),
        subsplease: bool = typer.Option(True, "--subsplease", "-S"),
        ember: bool = typer.Option(False, "--ember", "-E")):
    filter = "Ember" if ember else "SubsPlease"

    qbt = ctx.obj["qbt_client"]
    qbt = qbittorrentapi.Client(
        host='http://seshat.lan',
        port=8080,
        VERIFY_WEBUI_CERTIFICATE=False
    )

    rules = qbt.rss_rules()
    if name in rules:
        matched = qbt.rss_matching_articles(name).get(filter, [])
        count = len(matched)
        print(f"Already have a rule for【[bright_blue]{name}[/bright_blue]】with {count} episode{'' if count == 1 else 's'}")
        exit(0)

    save_path = qbt.torrents_categories()[category]["savePath"] + "/" + name

    qbt.rss_set_rule(name, {
        "mustContain": name,
        "savePath": save_path,
        "assignedCategory": category,
        "affectedFeeds": [qbt.rss_items()[filter]["url"]],
        "smartFilter": True
    })

    print(f"Successfully added rule for【[bright_blue]{name}[/bright_blue]】")

    if filter == "SubsPlease":
        count = 0
        matched = []
        search = requests.get("https://subsplease.org/api/", params={"f": "search", "tz": "America/Denver", "s": name}).json()
        for episode in search.values():
            for d in episode["downloads"]:
                if d["res"] == "1080":
                    matched.append(f"{episode['show']} - {episode['episode']}")
                    qbt.torrents_add(d["magnet"], category=category, save_path=save_path)
                    count += 1
                    continue
    else:
        matched = qbt.rss_matching_articles(name).get(filter, [])
        count = len(matched)

    if count == 0:
        print("No episodes found yet.")
    else:
        print(f"{count} episode{'' if count == 1 else 's'} added and downloading:")
        for match in matched:
            print(f"[bright_green]{match}[/bright_green]")

@app.command()
def list(ctx: typer.Context):
    qbt = ctx.obj["qbt_client"]


@app.callback()
def callback(ctx: typer.Context):
    """
    Adds RSS rules to follow new anime releases.
    """
    ctx.obj["qbt_client"] = qbittorrentapi.Client(
        host='http://seshat.lan',
        port=8080,
        VERIFY_WEBUI_CERTIFICATE=False
    )


if __name__ == "__main__":
    app(obj={})