"""Channel command for cli-web-youtube."""

from __future__ import annotations

import click

from ..core.client import YouTubeClient
from ..utils.helpers import handle_errors, print_json, resolve_json_mode
from ..utils.output import print_channel_detail


@click.group("channel")
def channel_group():
    """Browse YouTube channels."""


@channel_group.command("get")
@click.argument("handle")
@click.option("--json", "use_json", is_flag=True, help="Output as JSON.")
def channel_get(handle, use_json):
    """Get channel info and recent videos.

    HANDLE can be @username, channel ID (UC...), or URL.

    Example: channel get @MrBeast
    """
    # Extract handle from URL if needed
    if "youtube.com" in handle:
        if "/@" in handle:
            handle = handle.split("/@")[1].split("/")[0]
            handle = f"@{handle}"
        elif "/channel/" in handle:
            handle = handle.split("/channel/")[1].split("/")[0]

    use_json = resolve_json_mode(use_json)
    with handle_errors(json_mode=use_json):
        client = YouTubeClient()
        result = client.channel(handle)
        if use_json:
            print_json(result)
        else:
            print_channel_detail(result)
