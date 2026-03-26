"""Collections commands for cli-web-pexels."""

import click

from ..core.client import PexelsClient
from ..utils.helpers import handle_errors
from ..utils.output import (
    print_collection_detail,
    print_collections_table,
    print_json,
    print_pagination,
    print_photos_table,
)


@click.group("collections")
@click.pass_context
def collections(ctx):
    """Browse and explore Pexels collections."""
    pass


@collections.command()
@click.argument("slug")
@click.option("--page", type=int, default=1, help="Page number.")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON.")
@click.pass_context
def get(ctx, slug, page, json_mode):
    """Get collection detail and media by slug."""
    json_mode = json_mode or ctx.obj.get("json", False)
    with handle_errors(json_mode):
        client = PexelsClient()
        result = client.get_collection(slug, page=page)
        if json_mode:
            print_json(result)
        else:
            print_collection_detail(result["collection"])
            media = result.get("media", {})
            if media.get("data"):
                print_photos_table(media["data"])
                print_pagination(media.get("pagination", {}))


@collections.command()
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON.")
@click.pass_context
def discover(ctx, json_mode):
    """Show popular and curated collections from the discover page."""
    json_mode = json_mode or ctx.obj.get("json", False)
    with handle_errors(json_mode):
        client = PexelsClient()
        result = client.discover()
        if json_mode:
            print_json(result)
        else:
            if result.get("popular"):
                click.echo("\n  Popular Collections")
                click.echo(f"  {'─' * 40}")
                print_collections_table(result["popular"])
            if result.get("collections"):
                click.echo("\n  Curated Collections")
                click.echo(f"  {'─' * 40}")
                print_collections_table(result["collections"])
