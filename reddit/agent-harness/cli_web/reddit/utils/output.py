"""Output formatting for cli-web-reddit."""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

console = Console()


def post_table(posts: list[dict], title: str = "Posts") -> None:
    """Print a Rich table of post summaries."""
    table = Table(title=title, show_lines=False)
    table.add_column("Score", justify="right", style="yellow", no_wrap=True)
    table.add_column("Title", max_width=50)
    table.add_column("Sub", style="cyan", no_wrap=True)
    table.add_column("Author", style="green")
    table.add_column("Comments", justify="right")
    table.add_column("Flair", style="magenta")

    for p in posts:
        table.add_row(
            str(p.get("score", 0)),
            _trunc(p.get("title", ""), 50),
            p.get("subreddit", ""),
            p.get("author", ""),
            str(p.get("num_comments", 0)),
            _trunc(p.get("flair", ""), 15),
        )
    console.print(table)


def comment_table(comments: list[dict], title: str = "Comments") -> None:
    """Print a Rich table of comment summaries."""
    table = Table(title=title, show_lines=True)
    table.add_column("Score", justify="right", style="yellow", no_wrap=True)
    table.add_column("Author", style="green", no_wrap=True)
    table.add_column("Comment", max_width=60)
    table.add_column("OP", justify="center")

    for c in comments:
        indent = "  " * c.get("depth", 0)
        table.add_row(
            str(c.get("score", 0)),
            c.get("author", ""),
            _trunc(f"{indent}{c.get('body', '')}", 60),
            "OP" if c.get("is_submitter") else "",
        )
    console.print(table)


def subreddit_table(subs: list[dict], title: str = "Subreddits") -> None:
    """Print a Rich table of subreddit summaries."""
    table = Table(title=title, show_lines=False)
    table.add_column("Name", style="cyan")
    table.add_column("Title", max_width=35)
    table.add_column("Subscribers", justify="right", style="yellow")
    table.add_column("Description", max_width=40)

    for s in subs:
        table.add_row(
            f"r/{s.get('name', '')}",
            _trunc(s.get("title", ""), 35),
            f"{s.get('subscribers', 0):,}",
            _trunc(s.get("description", ""), 40),
        )
    console.print(table)


def subreddit_detail_display(info: dict) -> None:
    """Print detailed subreddit information."""
    click.echo(f"\n  r/{info.get('name')}")
    click.echo(f"  Title: {info.get('title')}")
    click.echo(f"  Subscribers: {info.get('subscribers', 0):,}")
    click.echo(f"  Active users: {info.get('active_users', 0):,}")
    click.echo(f"  Type: {info.get('type')}")
    click.echo(f"  Created: {info.get('created')}")
    if info.get("over_18"):
        click.echo("  NSFW: Yes")
    desc = info.get("description", "")
    if desc:
        click.echo(f"  Description: {desc[:200]}")
    click.echo(f"  URL: {info.get('url')}")
    click.echo()


def user_detail_display(info: dict) -> None:
    """Print detailed user information."""
    click.echo(f"\n  u/{info.get('name')}")
    click.echo(f"  Total karma: {info.get('total_karma', 0):,}")
    click.echo(f"  Link karma: {info.get('link_karma', 0):,}")
    click.echo(f"  Comment karma: {info.get('comment_karma', 0):,}")
    click.echo(f"  Created: {info.get('created')}")
    if info.get("is_gold"):
        click.echo("  Gold: Yes")
    if info.get("verified"):
        click.echo("  Verified email: Yes")
    click.echo(f"  URL: {info.get('url')}")
    click.echo()


def post_detail_display(post: dict) -> None:
    """Print detailed post information."""
    click.echo(f"\n  {post.get('title')}")
    click.echo(f"  r/{post.get('subreddit')} · u/{post.get('author')} · {post.get('created')}")
    click.echo(f"  Score: {post.get('score', 0):,}  ({post.get('upvote_ratio', 0):.0%} upvoted)")
    click.echo(f"  Comments: {post.get('num_comments', 0):,}")
    if post.get("flair"):
        click.echo(f"  Flair: {post['flair']}")
    if post.get("is_self") and post.get("selftext"):
        text = post["selftext"][:500]
        click.echo(f"\n  {text}")
        if len(post["selftext"]) > 500:
            click.echo("  ...")
    elif not post.get("is_self"):
        click.echo(f"  Link: {post.get('url')}")
    click.echo(f"  Permalink: {post.get('permalink')}")
    click.echo()


def _trunc(text: str | None, length: int) -> str:
    if not text:
        return ""
    text = text.replace("\n", " ").strip()
    return text[:length] + "..." if len(text) > length else text
