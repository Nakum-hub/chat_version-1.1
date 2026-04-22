from html import unescape
from pathlib import Path
import re
from typing import Literal

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import BACKEND_ROOT
from app.core.errors import AppError
from app.models.site import ContactProfile

TITLE_TAG_RE = re.compile(r"<title>(.*?)</title>", flags=re.IGNORECASE | re.DOTALL)
ASTRO_TITLE_PROP_RE = re.compile(
    r"<BaseLayout\b[^>]*\btitle\s*=\s*['\"]([^'\"]+)['\"]",
    flags=re.IGNORECASE | re.DOTALL,
)
ASTRO_DESCRIPTION_PROP_RE = re.compile(
    r"<BaseLayout\b[^>]*\bdescription\s*=\s*['\"]([^'\"]+)['\"]",
    flags=re.IGNORECASE | re.DOTALL,
)
HEADING_RE = re.compile(r"<h([1-2])\b[^>]*>(.*?)</h\1>", flags=re.IGNORECASE | re.DOTALL)
PARAGRAPH_RE = re.compile(r"<p\b[^>]*>(.*?)</p>", flags=re.IGNORECASE | re.DOTALL)
MAIN_RE = re.compile(r"<main\b[^>]*>(.*?)</main>", flags=re.IGNORECASE | re.DOTALL)
META_TAG_RE = re.compile(r"<meta\b[^>]*>", flags=re.IGNORECASE)
META_DESCRIPTION_NAME_RE = re.compile(r"\bname\s*=\s*['\"]description['\"]", flags=re.IGNORECASE)
META_CONTENT_RE = re.compile(r"\bcontent\s*=\s*['\"]([^'\"]+)['\"]", flags=re.IGNORECASE | re.DOTALL)

SEARCH_ENTRY_OVERRIDES: dict[str, dict[str, object]] = {
    "/": {
        "kind": "Overview",
        "keywords": (
            "Cybersecurity",
            "IT Solutions",
            "Managed Security",
            "Compliance",
            "Advisory",
        ),
        "text": "Purpose-Built Security | End-to-End Coverage | Rapid Response",
    },
    "/about": {
        "kind": "Company",
        "keywords": ("About", "Mission", "Vision", "Company"),
        "text": "Our Mission | Our Vision | Our Core Values | Why Choose Cyberfyx",
    },
    "/services": {
        "kind": "Solutions",
        "keywords": (
            "Services",
            "Solutions",
            "Cybersecurity",
            "IT Security",
            "Endpoint Management",
            "Training",
        ),
        "text": "Cybersecurity | Endpoint Management | IT Security | Core Industry Services | Training",
    },
    "/services/cybersecurity": {
        "kind": "Service",
        "keywords": (
            "Cybersecurity",
            "VAPT",
            "VA PT",
            "Vulnerability Assessment",
            "Penetration Testing",
            "GRC",
            "PCI DSS",
            "PCIDSS",
            "GDPR",
            "CCPA",
            "DPDPA",
            "vCISO",
            "VCISO",
            "DPO",
            "Virtual CISO",
            "Red Team",
            "SOC",
            "SOC 2",
            "SOC2",
            "HIPAA",
            "HIPPA",
            "CMMI",
        ),
        "text": "VAPT | GRC Maintenance | PCI DSS Readiness | vCISO and DPO | GDPR CCPA DPDPA | Red Team | SOC 2 | HIPAA | CMMI",
    },
    "/services/it-security": {
        "kind": "Service",
        "keywords": (
            "IT Security",
            "ISO 27001",
            "ISO27001",
            "ISO 27701",
            "ISO27701",
            "ISO 22301",
            "ISO22301",
            "ISO 20000",
            "ISO20000",
            "ISO 27017",
            "ISO27017",
            "ISO 27018",
            "ISO27018",
            "ISO 42001",
            "ISO42001",
            "CSA STAR",
            "TISAX",
            "Internal Audit",
            "Cloud Security",
            "Privacy",
        ),
        "text": "ISO 27001 | ISO 27701 | ISO 22301 | ISO 20000 | ISO 27017 and 27018 | ISO 42001 | CSA STAR | TISAX | Internal Audits",
    },
    "/services/endpoint-management": {
        "kind": "Service",
        "keywords": (
            "Endpoint Management",
            "UEM",
            "MDM",
            "IPM+",
            "IPM",
            "SIEM",
            "NOC",
            "Backup",
            "SmartDC",
            "Datacenter",
            "Device Management",
            "Monitoring",
        ),
        "text": "Unified Endpoint Management | Monitoring | SmartDC | SIEM | Cloud | NOC | Backup Solutions",
    },
    "/services/core-industry": {
        "kind": "Service",
        "keywords": (
            "Core Industry Services",
            "ISO 9001",
            "ISO9001",
            "ISO 14001",
            "ISO14001",
            "ISO 45001",
            "ISO45001",
            "AS9100",
            "IATF 16949",
            "IATF16949",
            "SEDEX",
            "SMETA",
            "FSC",
            "Fire Safety Audit",
        ),
        "text": "ISO 9001 | ISO 14001 | ISO 45001 | AS9100 | IATF 16949 | Fire Safety Audit | FSC Audit | SEDEX SMETA",
    },
    "/services/training": {
        "kind": "Service",
        "keywords": (
            "Training",
            "Security Awareness",
            "ISO 27001 Training",
            "GDPR Training",
            "HIPAA Training",
            "PCI DSS Training",
            "NIST CSF",
            "Business Continuity",
            "Disaster Recovery",
            "Phishing",
        ),
        "text": "ISO 27001 Awareness | GDPR Workshop | HIPAA Security and Privacy | PCI DSS Readiness | NIST CSF | Business Continuity and Disaster Recovery",
    },
    "/industries": {
        "kind": "Industry",
        "keywords": (
            "Industries",
            "Healthcare",
            "Banking",
            "Finance",
            "Retail",
            "Manufacturing",
            "Government",
            "Telecom",
            "Logistics",
            "Education",
        ),
        "text": "Healthcare | Banking and Finance | Retail and E-Commerce | Manufacturing | Government and Public Sector | Telecom | Transport and Logistics",
    },
    "/careers": {
        "kind": "Careers",
        "keywords": ("Careers", "Jobs", "Hiring", "Apply", "Resume"),
        "text": "Open Positions | Senior Security Consultant | Endpoint Management Engineer | Penetration Tester | Security Operations Analyst",
    },
    "/contact": {
        "kind": "Contact",
        "keywords": ("Contact", "Get Quote", "Quote", "Inquiry", "Talk to Expert"),
        "text": "Get in Touch | Start the conversation | Tell us about your needs",
    },
}
SEARCH_KEYWORD_STOPWORDS = {
    "and",
    "at",
    "cyberfyx",
    "for",
    "from",
    "our",
    "the",
    "with",
}


def _published_contact_profile_query() -> Select[tuple[ContactProfile]]:
    return (
        select(ContactProfile)
        .where(ContactProfile.profile_key == "primary", ContactProfile.published.is_(True))
        .options(
            selectinload(ContactProfile.office_regions),
            selectinload(ContactProfile.interest_options),
        )
    )


def get_public_contact_profile(session: Session) -> ContactProfile:
    profile = session.scalar(_published_contact_profile_query())
    if profile is None:
        raise AppError(
            code="contact_profile_not_configured",
            message="The public contact profile is not configured.",
            status_code=503,
        )
    return profile


def resolve_frontend_root() -> Path | None:
    candidates = (
        BACKEND_ROOT.parent / "frontend-astro" / "dist",
        BACKEND_ROOT / "frontend",
        BACKEND_ROOT.parent / "frontend",
    )
    for candidate in candidates:
        if candidate.is_dir() and (candidate / "index.html").is_file():
            return candidate
    return None


def resolve_search_root() -> tuple[Path, Literal["built", "source"]] | None:
    candidates: tuple[tuple[Path, Literal["built", "source"]], ...] = (
        (BACKEND_ROOT.parent / "frontend-astro" / "src" / "pages", "source"),
        (BACKEND_ROOT.parent / "frontend-astro" / "dist", "built"),
        (BACKEND_ROOT / "frontend", "built"),
        (BACKEND_ROOT.parent / "frontend", "built"),
    )

    for candidate, source_kind in candidates:
        if source_kind == "built" and candidate.is_dir() and (candidate / "index.html").is_file():
            return candidate, source_kind
        if source_kind == "source" and candidate.is_dir() and any(candidate.rglob("*.astro")):
            return candidate, source_kind

    return None


def _normalize_text_value(value: str) -> str:
    return " ".join(unescape(value).split())


def _extract_title(raw_html: str, *, fallback: str) -> str:
    title_match = TITLE_TAG_RE.search(raw_html)
    if title_match:
        return _normalize_text_value(title_match.group(1))
    return fallback


def _extract_source_title(raw_source: str, *, fallback: str) -> str:
    title_match = ASTRO_TITLE_PROP_RE.search(raw_source)
    if title_match:
        return _normalize_text_value(title_match.group(1))
    return fallback


def _extract_page_text(raw_markup: str) -> str:
    without_comments = re.sub(r"<!--.*?-->", " ", raw_markup, flags=re.DOTALL)
    without_scripts = re.sub(r"<script\b[^>]*>.*?</script>", " ", without_comments, flags=re.IGNORECASE | re.DOTALL)
    without_styles = re.sub(r"<style\b[^>]*>.*?</style>", " ", without_scripts, flags=re.IGNORECASE | re.DOTALL)
    without_tags = re.sub(r"<[^>]+>", " ", without_styles)
    return _normalize_text_value(without_tags)


def _extract_main_fragment(raw_html: str) -> str:
    main_match = MAIN_RE.search(raw_html)
    if main_match:
        return main_match.group(1)
    return raw_html


def _extract_meta_description(raw_html: str) -> str | None:
    for meta_match in META_TAG_RE.finditer(raw_html):
        meta_tag = meta_match.group(0)
        if not META_DESCRIPTION_NAME_RE.search(meta_tag):
            continue

        content_match = META_CONTENT_RE.search(meta_tag)
        if content_match:
            return _normalize_text_value(content_match.group(1))

    return None


def _extract_source_description(raw_source: str) -> str | None:
    description_match = ASTRO_DESCRIPTION_PROP_RE.search(raw_source)
    if description_match:
        return _normalize_text_value(description_match.group(1))
    return None


def _extract_headings(raw_markup: str) -> list[str]:
    headings: list[str] = []
    for match in HEADING_RE.finditer(raw_markup):
        heading_text = _extract_page_text(match.group(2))
        if heading_text and heading_text not in headings:
            headings.append(heading_text)
    return headings


def _extract_first_paragraph(raw_markup: str) -> str | None:
    for match in PARAGRAPH_RE.finditer(raw_markup):
        paragraph_text = _extract_page_text(match.group(1))
        if paragraph_text:
            return paragraph_text
    return None


def _build_search_keywords(href: str, title: str, section: str) -> list[str]:
    keywords: list[str] = []
    seen: set[str] = set()

    def add_keyword(keyword: str) -> None:
        normalized = _normalize_text_value(keyword).lower()
        display = _normalize_text_value(keyword)
        if normalized and normalized not in seen:
            seen.add(normalized)
            keywords.append(display)

    override = SEARCH_ENTRY_OVERRIDES.get(href, {})
    for keyword in override.get("keywords", ()):
        add_keyword(keyword)

    for part in href.strip("/").split("/"):
        if not part or part == "services":
            continue
        add_keyword(part.replace("-", " "))

    for token in re.findall(r"[a-z0-9]+", f"{title} {section}".lower()):
        if len(token) <= 2 or token in SEARCH_KEYWORD_STOPWORDS:
            continue
        add_keyword(token)

    return keywords


def _search_entry_kind(href: str) -> str:
    override = SEARCH_ENTRY_OVERRIDES.get(href, {})
    kind = override.get("kind")
    if isinstance(kind, str) and kind:
        return kind

    if href.startswith("/services/"):
        return "Service"
    if href == "/services":
        return "Solutions"
    if href == "/industries":
        return "Industry"
    if href == "/careers":
        return "Careers"
    if href == "/contact":
        return "Contact"
    if href == "/about":
        return "Company"
    return "Page"


def _iter_built_search_documents(frontend_root: Path) -> list[Path]:
    documents: list[Path] = []
    root_index = frontend_root / "index.html"
    if root_index.is_file():
        documents.append(root_index)

    for document in sorted(frontend_root.rglob("index.html"), key=lambda path: path.as_posix().lower()):
        if document == root_index:
            continue
        relative_parts = document.relative_to(frontend_root).parts
        if any(part.startswith("_") for part in relative_parts):
            continue
        documents.append(document)

    return documents


def _iter_source_search_documents(frontend_root: Path) -> list[Path]:
    documents: list[Path] = []
    for document in sorted(frontend_root.rglob("*.astro"), key=lambda path: path.as_posix().lower()):
        relative_parts = document.relative_to(frontend_root).parts
        if any(part.startswith("_") or "[" in part or "]" in part for part in relative_parts):
            continue
        documents.append(document)

    return documents


def _iter_search_documents(frontend_root: Path, source_kind: Literal["built", "source"]) -> list[Path]:
    if source_kind == "source":
        return _iter_source_search_documents(frontend_root)
    return _iter_built_search_documents(frontend_root)


def _built_document_href(frontend_root: Path, document: Path) -> str:
    relative_path = document.relative_to(frontend_root).as_posix()
    if relative_path == "index.html":
        return "/"

    if relative_path.endswith("/index.html"):
        return f"/{relative_path[:-11].strip('/')}"

    return f"/{relative_path}"


def _source_document_href(frontend_root: Path, document: Path) -> str:
    relative = document.relative_to(frontend_root).with_suffix("")
    parts = list(relative.parts)

    if parts == ["index"]:
        return "/"
    if parts and parts[-1] == "index":
        parts = parts[:-1]

    return f"/{'/'.join(parts)}"


def _document_href(frontend_root: Path, document: Path, source_kind: Literal["built", "source"]) -> str:
    if source_kind == "source":
        return _source_document_href(frontend_root, document)
    return _built_document_href(frontend_root, document)


def _document_section(document: Path, href: str) -> str:
    if href == "/":
        return "Home"

    if document.name == "index.html" and len(document.parts) >= 2:
        return document.parent.name.replace("-", " ").title()

    if document.stem == "index" and document.parent != document.parent.parent:
        return document.parent.name.replace("-", " ").title()

    return document.stem.replace("-", " ").title()


def list_public_search_entries() -> list[dict[str, object]]:
    resolved_root = resolve_search_root()
    if resolved_root is None:
        raise AppError(
            code="site_search_not_available",
            message="The site search index is not available because the frontend files could not be found.",
            status_code=503,
        )

    frontend_root, source_kind = resolved_root
    documents = _iter_search_documents(frontend_root, source_kind)

    entries: list[dict[str, object]] = []
    for document in documents:
        if not document.is_file():
            continue

        raw_content = document.read_text(encoding="utf-8", errors="ignore")
        href = _document_href(frontend_root, document, source_kind)
        if href.startswith("/admin") or href == "/404":
            continue

        fallback_title = "Cyberfyx" if href == "/" else _document_section(document, href)
        section = _document_section(document, href)
        override = SEARCH_ENTRY_OVERRIDES.get(href, {})

        if source_kind == "source":
            fallback_display_title = _extract_source_title(raw_content, fallback=fallback_title)
            headings = _extract_headings(raw_content)
            excerpt = _extract_source_description(raw_content) or _extract_first_paragraph(raw_content)
        else:
            main_fragment = _extract_main_fragment(raw_content)
            fallback_display_title = _extract_title(raw_content, fallback=fallback_title)
            headings = _extract_headings(main_fragment)
            excerpt = _extract_meta_description(raw_content) or _extract_first_paragraph(main_fragment)

        override_title = override.get("title")
        override_excerpt = override.get("excerpt")
        override_text = override.get("text")

        title = override_title if isinstance(override_title, str) and override_title else (
            headings[0] if headings else fallback_display_title
        )
        remaining_headings = [heading for heading in headings[1:] if heading != title]
        text = override_text if isinstance(override_text, str) else " ".join(remaining_headings)
        display_excerpt = override_excerpt if isinstance(override_excerpt, str) else excerpt

        entries.append(
            {
                "href": href,
                "title": title,
                "kind": _search_entry_kind(href),
                "section": section,
                "text": text,
                "excerpt": display_excerpt,
                "keywords": _build_search_keywords(href, title, section),
            }
        )

    return entries
