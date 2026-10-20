import os
import re
import json
import requests
import sys


MEDIUM_USERNAME = "viveknaskar"
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



def format_count(count):
    if count >= 1_000_000:
        m = count / 1_000_000
        return f"{m:.1f}M".replace(".0M", "M")
    if count >= 1000:
        k = count / 1000
        return f"{k:.1f}K".replace(".0K", "K")
    return str(count)


def update_readme(medium_count):
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

    if content != original:
        with open(README_PATH, "w") as f:
            f.write(content)
        print("README updated.")
    else:
        print("No changes to README.")


if __name__ == "__main__":
    medium_count = get_medium_followers()

    if medium_count is None:
        print("Could not fetch Medium followers. Exiting without changes.")
        sys.exit(0)

    update_readme(medium_count)
