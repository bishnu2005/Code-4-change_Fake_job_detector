"""
URL Legitimacy Verification Module
Analyzes job posting URLs for phishing, impersonation, and suspicious patterns.
"""

import re
import socket
from urllib.parse import urlparse
from typing import Dict, List, Optional

# ── Free hosting / suspicious TLD domains ────────────────────────────────
FREE_HOSTING_DOMAINS = {
    "blogspot.com", "blogspot.in", "wixsite.com", "weebly.com",
    "wordpress.com", "carrd.co", "sites.google.com", "github.io",
    "netlify.app", "herokuapp.com", "000webhostapp.com",
    "wix.com", "squarespace.com", "jimdosite.com",
    "godaddysites.com", "my.canva.site", "notion.site",
}

# ── Suspicious URL keywords ──────────────────────────────────────────────
SUSPICIOUS_URL_KEYWORDS = [
    "secure-login", "verify-account", "apply-now-fast", "limited-offer",
    "crypto-invest", "free-money", "wire-transfer", "urgent-apply",
    "click-here", "confirm-identity", "reset-password", "signin",
    "account-verify", "update-payment", "free-iphone",
]

# ── Suspicious domain keywords (phishing signals in the domain itself) ───
SUSPICIOUS_DOMAIN_KEYWORDS = {
    "secure", "verify", "login", "payout", "crypto",
    "signin", "confirm", "update", "account", "password",
}

# ── Leet-speak map ───────────────────────────────────────────────────────
LEET_MAP = {
    "0": "o", "1": "l", "3": "e", "4": "a",
    "5": "s", "7": "t", "8": "b", "9": "g",
}

# ── IP address regex ─────────────────────────────────────────────────────
IP_REGEX = re.compile(
    r"^(?:\d{1,3}\.){3}\d{1,3}$"
)

# ── Company name stopwords ───────────────────────────────────────────────
COMPANY_STOPWORDS = {
    "inc", "ltd", "llc", "corp", "corporation", "company",
    "co", "group", "holdings", "international", "pvt",
    "private", "limited", "the", "and", "technologies",
    "systems", "solutions", "services", "consulting",
    "global", "enterprises", "foundation",
}

# ── Known multi-part TLDs ────────────────────────────────────────────────
MULTI_TLDS = {
    "co.uk", "co.in", "co.jp", "co.kr", "co.za", "co.nz",
    "com.au", "com.br", "com.cn", "com.sg", "com.hk",
    "org.uk", "net.au", "ac.uk", "ac.in", "gov.uk",
}


def normalize_url(url: str) -> str:
    """Ensure URL has a scheme."""
    url = url.strip()
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def extract_root_domain(hostname: str) -> str:
    """
    Extract the root domain from a hostname, handling:
    - www prefix
    - multi-part TLDs (.co.uk, .com.au)
    - subdomains
    
    Examples:
        www.infosys.com → infosys
        careers.google.com → google
        jobs.amazon.co.uk → amazon
        sub1.sub2.example.net → example
    """
    if not hostname:
        return ""

    hostname = hostname.lower().strip()

    # Remove www. prefix
    if hostname.startswith("www."):
        hostname = hostname[4:]

    parts = hostname.split(".")

    # Check for multi-part TLDs
    if len(parts) >= 3:
        potential_multi = ".".join(parts[-2:])
        if potential_multi in MULTI_TLDS:
            # root domain is the part before the multi-TLD
            return parts[-3] if len(parts) >= 3 else parts[0]

    # Standard: root domain is second-to-last part
    if len(parts) >= 2:
        return parts[-2]

    return parts[0]


def parse_url_parts(url: str) -> Dict:
    """Parse URL into components."""
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()

    # Remove www for subdomain counting
    clean_host = hostname
    if clean_host.startswith("www."):
        clean_host = clean_host[4:]

    parts = clean_host.split(".")

    # Extract root domain properly
    root = extract_root_domain(hostname)

    # Count real subdomains (exclude www and the domain+TLD)
    if len(parts) >= 3:
        # Check multi-TLD
        potential_multi = ".".join(parts[-2:])
        if potential_multi in MULTI_TLDS:
            subdomains = parts[:-3]
        else:
            subdomains = parts[:-2]
    else:
        subdomains = []

    tld = parts[-1] if parts else ""

    return {
        "full_url": url,
        "scheme": parsed.scheme,
        "hostname": hostname,
        "root_domain": root,
        "tld": tld,
        "subdomains": subdomains,
        "path": parsed.path,
    }


def is_ip_based(hostname: str) -> bool:
    """Check if hostname is an IP address."""
    return bool(IP_REGEX.match(hostname))


def is_free_hosting(hostname: str) -> bool:
    """Check if URL uses a free hosting provider."""
    for free_domain in FREE_HOSTING_DOMAINS:
        if hostname.endswith(free_domain):
            return True
    return False


def detect_suspicious_keywords(url: str) -> List[str]:
    """Find suspicious keywords in the URL."""
    url_lower = url.lower()
    return [kw for kw in SUSPICIOUS_URL_KEYWORDS if kw in url_lower]


def has_excessive_subdomains(subdomains: list) -> bool:
    """Flag if URL has 3+ real subdomains (www already excluded)."""
    return len(subdomains) >= 3


def has_long_domain(hostname: str) -> bool:
    """Flag very long hostnames."""
    return len(hostname) > 40


def has_numeric_substitutions(hostname: str) -> bool:
    """
    Detect leet-speak in hostname — only flag when a digit appears
    adjacent to or within what looks like an alpha word (impersonation).
    Does NOT flag purely numeric subdomains or port-like patterns.
    """
    # Get root domain + subdomains, skip TLD
    base = hostname.rsplit(".", 1)[0] if "." in hostname else hostname

    # Remove www
    if base.startswith("www."):
        base = base[4:]

    # Split into segments by dots and hyphens
    segments = re.split(r"[.\-]", base)

    for seg in segments:
        # Skip purely numeric segments (e.g., "123", port numbers)
        if seg.isdigit():
            continue
        # Skip purely alpha segments
        if seg.isalpha():
            continue
        # Mixed alpha+digit — potential leet-speak
        if seg and any(c.isdigit() for c in seg) and any(c.isalpha() for c in seg):
            return True

    return False


def decode_leet(text: str) -> str:
    """Convert leet-speak back to normal."""
    return "".join(LEET_MAP.get(ch, ch) for ch in text)


def normalize_company_name(name: str) -> str:
    """Normalize company name for comparison — strip stopwords, punctuation, spaces."""
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9\s]", "", name)
    words = [w for w in name.split() if w not in COMPANY_STOPWORDS]
    return "".join(words)


def _simple_similarity(a: str, b: str) -> float:
    """
    Lightweight similarity score (0.0–1.0) based on longest common substring ratio.
    No external dependencies needed.
    """
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0

    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)

    # Find longest common substring
    best = 0
    for i in range(len(shorter)):
        for j in range(i + 1, len(shorter) + 1):
            substr = shorter[i:j]
            if substr in longer and len(substr) > best:
                best = len(substr)

    # Similarity = LCS length / average length
    avg_len = (len(a) + len(b)) / 2
    return best / avg_len if avg_len > 0 else 0.0


def check_domain_company_match(hostname: str, company_name: str) -> str:
    """
    Compare URL root domain against company name.
    Returns confidence level: "HIGH", "MEDIUM", or "LOW".

    HIGH   = clearly matches (no risk added)
    MEDIUM = partial/uncertain match (+10 risk)
    LOW    = clear mismatch (+20 risk)
    """
    if not company_name or not company_name.strip():
        return "HIGH"  # Can't verify → assume OK

    norm_company = normalize_company_name(company_name)
    root = extract_root_domain(hostname)
    root_clean = re.sub(r"[^a-z0-9]", "", root)
    decoded_root = decode_leet(root_clean)

    if not norm_company or not root_clean:
        return "HIGH"

    # ── Exact match ──────────────────────────────────────────────────
    if norm_company == root_clean or norm_company == decoded_root:
        return "HIGH"

    # ── Substring containment (either direction) ─────────────────────
    if norm_company in root_clean or root_clean in norm_company:
        return "HIGH"
    if norm_company in decoded_root or decoded_root in norm_company:
        return "HIGH"

    # ── Prefix match (first 4+ chars) ────────────────────────────────
    min_prefix = min(len(norm_company), len(root_clean), 4)
    if min_prefix >= 4:
        if norm_company[:min_prefix] == root_clean[:min_prefix]:
            return "HIGH"
        if norm_company[:min_prefix] == decoded_root[:min_prefix]:
            return "HIGH"

    # ── Similarity score ─────────────────────────────────────────────
    sim = _simple_similarity(norm_company, root_clean)
    sim_decoded = _simple_similarity(norm_company, decoded_root)
    best_sim = max(sim, sim_decoded)

    if best_sim >= 0.8:
        return "HIGH"
    elif best_sim >= 0.5:
        return "MEDIUM"

    return "LOW"


def check_dns(hostname: str) -> bool:
    """Lightweight DNS check — returns True if domain resolves."""
    if not hostname or is_ip_based(hostname):
        return True  # IPs resolve by definition
    try:
        socket.setdefaulttimeout(3)
        socket.gethostbyname(hostname)
        return True
    except (socket.gaierror, socket.timeout, OSError):
        return False


def try_scrape_meta(url: str) -> Dict:
    """
    Optional lightweight scrape: page title + meta description.
    Returns dict with scraped info and status.
    """
    result = {
        "reachable": False,
        "status_code": None,
        "page_title": "",
        "meta_description": "",
        "ssl_error": False,
    }

    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return result

    try:
        resp = requests.get(url, timeout=5, allow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 FakeJobDetector/1.0"
        })
        result["status_code"] = resp.status_code

        if resp.status_code == 200:
            result["reachable"] = True
            soup = BeautifulSoup(resp.text[:10000], "html.parser")
            title_tag = soup.find("title")
            if title_tag:
                result["page_title"] = title_tag.get_text(strip=True)[:200]
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                result["meta_description"] = (meta_desc.get("content") or "")[:300]
    except Exception as e:
        err_str = str(e).lower()
        if "ssl" in err_str or "certificate" in err_str:
            result["ssl_error"] = True

    return result


def analyze_url(url: str, company_name: str = "") -> Dict:
    """
    Full URL legitimacy analysis.
    Returns structured dict for risk_breakdown.url_analysis.
    """
    result = {
        "url_provided": False,
        "url": "",
        "domain": "",
        "ip_based": False,
        "free_hosting": False,
        "suspicious_keywords": [],
        "domain_matches_company": True,
        "excessive_subdomains": False,
        "long_domain": False,
        "numeric_substitutions": False,
        "dns_resolves": True,
        "ssl_error": False,
        "reachable": False,
        "url_risk_score": 0,
    }

    if not url or not url.strip():
        return result

    url = normalize_url(url)
    parts = parse_url_parts(url)
    hostname = parts["hostname"]

    result["url_provided"] = True
    result["url"] = url
    result["domain"] = hostname

    # ── Checks ───────────────────────────────────────────────────────
    risk = 0

    # IP-based URL
    if is_ip_based(hostname):
        result["ip_based"] = True
        risk += 30

    # Free hosting
    if is_free_hosting(hostname):
        result["free_hosting"] = True
        risk += 25

    # Suspicious keywords
    sus_kw = detect_suspicious_keywords(url)
    if sus_kw:
        result["suspicious_keywords"] = sus_kw
        risk += min(len(sus_kw) * 8, 15)

    # Excessive subdomains (www already excluded)
    if has_excessive_subdomains(parts["subdomains"]):
        result["excessive_subdomains"] = True
        risk += 10

    # Long domain
    if has_long_domain(hostname):
        result["long_domain"] = True
        risk += 10

    # Numeric substitutions (smart detection)
    if has_numeric_substitutions(hostname):
        result["numeric_substitutions"] = True
        risk += 15

    # Company name match — now uses confidence levels
    match_confidence = check_domain_company_match(hostname, company_name)
    if match_confidence == "LOW":
        result["domain_matches_company"] = False
        risk += 20
    elif match_confidence == "MEDIUM":
        result["domain_matches_company"] = True  # don't flag visually
        risk += 10

    # DNS check
    if not is_ip_based(hostname):
        resolves = check_dns(hostname)
        result["dns_resolves"] = resolves
        if not resolves:
            risk += 25

    # Optional scrape
    scrape = try_scrape_meta(url)
    result["ssl_error"] = scrape.get("ssl_error", False)
    result["reachable"] = scrape.get("reachable", False)
    if scrape.get("ssl_error"):
        risk += 15
    if result["url_provided"] and not scrape.get("reachable", False):
        risk += 10

    # Cap risk contribution
    result["url_risk_score"] = min(risk, 40)

    return result
