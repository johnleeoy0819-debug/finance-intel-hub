"""Fetch publication metadata from arXiv and CrossRef (DOI)."""
import logging
import re
from typing import Any, Dict, Optional

import requests
import feedparser

logger = logging.getLogger(__name__)


def _extract_arxiv_id(url: str) -> Optional[str]:
    """Extract arXiv ID from URL like https://arxiv.org/abs/2401.00001"""
    match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d+\.\d+)(?:\.pdf)?', url)
    if match:
        return match.group(1)
    # Bare arxiv id
    if re.match(r'^\d{4}\.\d{4,5}$', url):
        return url
    return None


def _clean_doi(url: str) -> Optional[str]:
    """Extract DOI from URL or string."""
    match = re.search(r'10\.\d{4,}/[^\s]+', url)
    if match:
        return match.group(0).rstrip('.,;')
    return None


def fetch_arxiv(arxiv_id: str) -> Dict[str, Any]:
    """Fetch metadata from arXiv API."""
    url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)
    if not feed.entries:
        raise ValueError(f"arXiv paper not found: {arxiv_id}")

    entry = feed.entries[0]
    authors = [a.get("name", "") for a in entry.get("authors", [])]
    # Try to get PDF link
    pdf_url = None
    for link in entry.get("links", []):
        if link.get("type") == "application/pdf":
            pdf_url = link.get("href")
            break

    return {
        "pub_type": "arxiv",
        "title": entry.get("title", "").replace("\n", " ").strip(),
        "authors": ", ".join(authors),
        "abstract": entry.get("summary", "").replace("\n", " ").strip(),
        "url": entry.get("link", ""),
        "pdf_url": pdf_url,
        "publication_date": entry.get("published", ""),
        "source": f"arxiv:{arxiv_id}",
    }


def fetch_doi(doi: str) -> Dict[str, Any]:
    """Fetch metadata from CrossRef API."""
    url = f"https://api.crossref.org/works/{doi}"
    headers = {"User-Agent": "FinanceIntelHub/1.0 (mailto:admin@example.com)"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()["message"]

    authors = []
    for a in data.get("author", []):
        name = f"{a.get('given', '')} {a.get('family', '')}".strip()
        if name:
            authors.append(name)

    return {
        "pub_type": "journal",
        "title": data.get("title", [""])[0],
        "authors": ", ".join(authors),
        "abstract": data.get("abstract", "").replace("<jats:p>", "").replace("</jats:p>", "").strip(),
        "publisher": data.get("publisher", ""),
        "doi": doi,
        "url": data.get("URL", f"https://doi.org/{doi}"),
        "publication_date": data.get("published-print", {}).get("date-parts", [[""]])[0][0] or "",
        "citation_count": data.get("is-referenced-by-count", 0),
        "source": f"doi:{doi}",
    }


def fetch_by_url(url: str) -> Dict[str, Any]:
    """Auto-detect arXiv or DOI and fetch metadata."""
    arxiv_id = _extract_arxiv_id(url)
    if arxiv_id:
        return fetch_arxiv(arxiv_id)

    doi = _clean_doi(url)
    if doi:
        return fetch_doi(doi)

    raise ValueError(f"Unsupported publication URL: {url}. Expected arXiv or DOI.")
