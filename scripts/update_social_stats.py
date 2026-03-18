import re
import json
import requests
import sys


MEDIUM_USERNAME = "viveknaskar"
X_USERNAME = "vivek_naskar"
BEEHIIV_SLUG = "savvymonk"
README_PATH = "README.md"


def get_medium_followers():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
    }
    try:
        url = f"https://medium.com/@{MEDIUM_USERNAME}?format=json"
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            text = response.text
            if "])}while(1);</p>" in text:
                text = text.replace("])}while(1);</p>", "")
            data = json.loads(text)
            user_id = data["payload"]["user"]["userId"]
            count = data["payload"]["references"]["SocialStats"][user_id]["followerCount"]
            print(f"Medium followers: {count}")
            return count
        else:
            print(f"Medium API returned status {response.status_code}")
    except Exception as e:
        print(f"Error fetching Medium followers: {e}")
    return None


def get_x_followers():
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()
            try:
                page.goto(
                    f"https://x.com/{X_USERNAME}",
                    wait_until="networkidle",
                    timeout=30000,
                )
                # Look for followers count in page content
                content = page.content()
                # X renders follower count as e.g. "3,245 Followers"
                match = re.search(r'"followers_count":\s*(\d+)', content)
                if not match:
                    match = re.search(r'([\d,]+)\s+Followers', content)
                if match:
                    raw = match.group(1).replace(",", "")
                    count = int(raw)
                    print(f"X followers: {count}")
                    return count
                else:
                    print("Could not find X follower count in page")
            finally:
                browser.close()
    except ImportError:
        print("Playwright not installed, skipping X followers")
    except Exception as e:
        print(f"Error fetching X followers: {e}")
    return None


def get_beehiiv_subscribers():
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()
            try:
                page.goto(
                    f"https://{BEEHIIV_SLUG}.beehiiv.com/",
                    wait_until="networkidle",
                    timeout=30000,
                )
                content = page.content()
                # Beehiiv shows subscriber count as e.g. "71 subscribers"
                match = re.search(r'([\d,]+)\s+subscribers', content, re.IGNORECASE)
                if match:
                    count = int(match.group(1).replace(",", ""))
                    print(f"Beehiiv subscribers: {count}")
                    return count
                else:
                    print("Could not find Beehiiv subscriber count in page")
            finally:
                browser.close()
    except ImportError:
        print("Playwright not installed, skipping Beehiiv subscribers")
    except Exception as e:
        print(f"Error fetching Beehiiv subscribers: {e}")
    return None


def format_count(count):
    if count >= 1_000_000:
        m = count / 1_000_000
        return f"{m:.1f}M".replace(".0M", "M")
    if count >= 1000:
        k = count / 1000
        return f"{k:.1f}K".replace(".0K", "K")
    return str(count)


def update_readme(medium_count, x_count, beehiiv_count):
    with open(README_PATH, "r") as f:
        content = f.read()

    original = content

    if medium_count is not None:
        formatted = format_count(medium_count)
        content = re.sub(
            r"(badge/Medium%20Followers-)[^-?]+(-black)",
            lambda m: f"{m.group(1)}{formatted}{m.group(2)}",
            content,
        )

    if x_count is not None:
        formatted = format_count(x_count)
        content = re.sub(
            r"(badge/X%20Followers-)[^-?]+(-black)",
            lambda m: f"{m.group(1)}{formatted}{m.group(2)}",
            content,
        )

    if beehiiv_count is not None:
        formatted = format_count(beehiiv_count)
        content = re.sub(
            r"(badge/Beehiiv%20Subscribers-)[^-?]+(-orange)",
            lambda m: f"{m.group(1)}{formatted}{m.group(2)}",
            content,
        )

    if content != original:
        with open(README_PATH, "w") as f:
            f.write(content)
        print("README updated.")
    else:
        print("No changes to README.")


if __name__ == "__main__":
    medium_count = get_medium_followers()
    x_count = get_x_followers()
    beehiiv_count = get_beehiiv_subscribers()

    if medium_count is None and x_count is None and beehiiv_count is None:
        print("Could not fetch any counts. Exiting without changes.")
        sys.exit(0)

    update_readme(medium_count, x_count, beehiiv_count)
