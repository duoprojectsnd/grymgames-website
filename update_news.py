"""One-time script to clear News table and add the 6 latest Steam news."""
import boto3
import os

# You can set these as env vars or paste them here temporarily
AWS_KEY = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
REGION = "us-east-1"
TABLE = "News"

dynamo = boto3.client(
    "dynamodb",
    region_name=REGION,
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
)

# Step 1: Clear all existing news
print("Clearing existing news...")
resp = dynamo.scan(TableName=TABLE)
for item in resp.get("Items", []):
    slug = item["slug"]["S"]
    dynamo.delete_item(TableName=TABLE, Key={"slug": {"S": slug}})
    print(f"  Deleted: {slug}")

# Step 2: Add the 6 latest news from Steam
news_items = [
    {
        "slug": {"S": "major-update-june-2026"},
        "title": {"S": "Gear Up, Stand Out: Deep Customization, Rebuilt Crafting, and the Dawn of Character Creation!"},
        "date": {"S": "2026-06-23"},
        "category": {"S": "update"},
        "excerpt": {"S": "OKUBI's biggest update adds Upgrade & Imbue systems, reworks crafting/rewards, debuts Character Creation, and overhauls matchmaking for faster queues and better global ping."},
        "image": {"S": "assets/news/major-update.jpg"},
        "content": {"S": "<p>OKUBI's biggest update is here! This patch introduces the <strong>Upgrade & Imbue</strong> systems, completely reworks crafting and rewards, debuts <strong>Character Creation</strong>, and overhauls matchmaking for faster queues and better global ping.</p><p>Jump in and experience the new systems firsthand.</p>"},
        "type": {"S": "news"},
    },
    {
        "slug": {"S": "playtest-weekend-april-2026"},
        "title": {"S": "The next OKUBI playtest is happening this weekend!"},
        "date": {"S": "2026-04-15"},
        "category": {"S": "playtest"},
        "excerpt": {"S": "Request access via Steam. Space is limited, so grab your seat before the gates close."},
        "image": {"S": "assets/news/playtest-april.jpg"},
        "content": {"S": "<p>Claim your spot today! The next OKUBI playtest is happening this weekend. Request access via Steam — space is limited, so grab your seat before the gates close.</p>"},
        "type": {"S": "news"},
    },
    {
        "slug": {"S": "kickstarter-launch-nov-2025"},
        "title": {"S": "The adventure expands — follow OKUBI on Kickstarter today."},
        "date": {"S": "2025-11-27"},
        "category": {"S": "announcement"},
        "excerpt": {"S": "Join the pre-launch page and smash the 'Notify me on launch' button for an exclusive reward."},
        "image": {"S": "assets/news/kickstarter.jpg"},
        "content": {"S": "<p>A big step forward! The adventure expands — follow OKUBI on Kickstarter today. Join the pre-launch page and smash the <em>Notify me on launch</em> button for an exclusive reward.</p>"},
        "type": {"S": "news"},
    },
    {
        "slug": {"S": "thank-you-july-2025"},
        "title": {"S": "THANK YOU! A retrospective on this weekend's event."},
        "date": {"S": "2025-07-21"},
        "category": {"S": "community"},
        "excerpt": {"S": "A look back at the incredible Alpha Weekend — thank you to everyone who showed up and made it unforgettable."},
        "image": {"S": "assets/news/thank-you.jpg"},
        "content": {"S": "<p>Thank you to everyone who joined us this weekend! The Alpha Weekend was an incredible experience and we're blown away by the community response. Here's a retrospective on the event.</p>"},
        "type": {"S": "news"},
    },
    {
        "slug": {"S": "alpha-peak-hour-july-2025"},
        "title": {"S": "ALPHA WEEKEND - Peak Hour!"},
        "date": {"S": "2025-07-20"},
        "category": {"S": "event"},
        "excerpt": {"S": "Everybody drops in at once! No queue, no delays. 2v2s and 3v3s on the menu!"},
        "image": {"S": "assets/news/peak-hour.jpg"},
        "content": {"S": "<p>Peak Hour is LIVE! Everybody drops in at once — no queue, no delays. 2v2s and 3v3s are on the menu. Get in there!</p>"},
        "type": {"S": "news"},
    },
    {
        "slug": {"S": "playtest-weekend-begun-july-2025"},
        "title": {"S": "OKUBI - PLAYTEST WEEKEND HAS BEGUN!"},
        "date": {"S": "2025-07-18"},
        "category": {"S": "playtest"},
        "excerpt": {"S": "Your first look at OKUBI's core experience. Jump in, claim your free Battlepass, and help us shape the future."},
        "image": {"S": "assets/news/playtest-weekend.jpg"},
        "content": {"S": "<p>OKUBI's first test season is live this weekend! Jump in, claim your free Battlepass, and help us shape the future. This is your first look at the core experience.</p>"},
        "type": {"S": "news"},
    },
]

print("\nAdding 6 news items...")
for item in news_items:
    dynamo.put_item(TableName=TABLE, Item=item)
    print(f"  Added: {item['slug']['S']}")

print("\nDone! 6 news articles are now live.")
