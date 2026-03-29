"""Data models for Code Wiki CLI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Repository:
    """A GitHub repository on Code Wiki."""

    slug: str
    github_url: str
    description: str = ""
    avatar_url: str = ""
    stars: int = 0
    commit_hash: str = ""
    updated_at: datetime | None = None

    @property
    def org(self) -> str:
        parts = self.slug.split("/")
        return parts[0] if len(parts) >= 2 else ""

    @property
    def name(self) -> str:
        parts = self.slug.split("/")
        return parts[1] if len(parts) >= 2 else self.slug

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "github_url": self.github_url,
            "description": self.description,
            "avatar_url": self.avatar_url,
            "stars": self.stars,
            "commit_hash": self.commit_hash,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class WikiSection:
    """A section in a Code Wiki page."""

    title: str
    level: int
    description: str = ""
    code_refs: list[str] = field(default_factory=list)
    content: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "level": self.level,
            "description": self.description,
            "code_refs": self.code_refs,
            "content": self.content,
        }


@dataclass
class WikiPage:
    """A full Code Wiki page for a repository."""

    repo: Repository
    sections: list[WikiSection] = field(default_factory=list)
    has_wiki: bool = False

    def to_dict(self) -> dict:
        return {
            "repo": self.repo.to_dict(),
            "sections": [s.to_dict() for s in self.sections],
            "section_count": len(self.sections),
            "has_wiki": self.has_wiki,
        }


@dataclass
class ChatResponse:
    """A Gemini chat response."""

    answer: str
    repo_slug: str

    def to_dict(self) -> dict:
        return {
            "answer": self.answer,
            "repo": self.repo_slug,
        }
