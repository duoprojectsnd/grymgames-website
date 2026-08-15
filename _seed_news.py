import json, os, boto3
from boto3.dynamodb.types import TypeSerializer

cfg_path = os.path.join(os.path.dirname(__file__), "website_config.json")
with open(cfg_path) as f:
    cfg = json.load(f)

key = os.environ.get("AWS_ACCESS_KEY_ID", cfg.get("aws_access_key_id", ""))
secret = os.environ.get("AWS_SECRET_ACCESS_KEY", cfg.get("aws_secret_access_key", ""))

if not key or not secret:
    print("ERROR: No AWS credentials.")
    exit(1)

dynamo = boto3.client("dynamodb", region_name="us-east-1", aws_access_key_id=key, aws_secret_access_key=secret)
ser = TypeSerializer()

images = [
    "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2118100/2b84f5d18ba9e7d3220f66bb2452f81d0a7468e0/ss_2b84f5d18ba9e7d3220f66bb2452f81d0a7468e0.1920x1080.jpg?t=1771880532",
    "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2118100/0af0df51dd6d49ad833d1c31da54951a4fd54024/ss_0af0df51dd6d49ad833d1c31da54951a4fd54024.1920x1080.jpg?t=1771880532",
    "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2118100/ss_d5e9eacb3154eb00e00c06333f0508f95b6409a0.1920x1080.jpg?t=1771880532",
    "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2118100/6aa4612bf582cd106b821c67c43e813867842ff4/ss_6aa4612bf582cd106b821c67c43e813867842ff4.1920x1080.jpg?t=1771880532",
    "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2118100/7565960bb62dd2b6dcf468a49f6bc2aa57abe4e4/ss_7565960bb62dd2b6dcf468a49f6bc2aa57abe4e4.1920x1080.jpg?t=1771880532",
]

posts = [
    {"slug": "test-2", "title": "Patch 0.4.0 — New Archetype", "date": "2026-07-26", "displayDate": "July 26, 2026", "category": "PATCH NOTES", "excerpt": "Introducing the Invoker class with elemental combo mechanics.", "image": images[0], "content": [{"type": "text", "value": "The Invoker joins the roster."}]},
    {"slug": "test-3", "title": "Arena Season 2 Begins", "date": "2026-07-25", "displayDate": "July 25, 2026", "category": "EVENT", "excerpt": "Ranked arena is back with new rewards and leaderboard resets.", "image": images[1], "content": [{"type": "text", "value": "Climb the ranks."}]},
    {"slug": "test-4", "title": "Community Spotlight: Week 12", "date": "2026-07-24", "displayDate": "July 24, 2026", "category": "NEWS", "excerpt": "The best clips, builds, and fan art from this week.", "image": images[2], "content": [{"type": "text", "value": "Great community content."}]},
    {"slug": "test-5", "title": "Dev Diary: Crafting Overhaul", "date": "2026-07-23", "displayDate": "July 23, 2026", "category": "DEV DIARY", "excerpt": "A complete rework of the crafting system with new recipes.", "image": images[3], "content": [{"type": "text", "value": "Crafting is evolving."}]},
    {"slug": "test-6", "title": "Kickstarter Update #3", "date": "2026-07-22", "displayDate": "July 22, 2026", "category": "ANNOUNCEMENT", "excerpt": "We hit our stretch goal! Heres whats unlocked.", "image": images[4], "content": [{"type": "text", "value": "Thank you backers!"}]},
]

for p in posts:
    item = {k: ser.serialize(v) for k, v in p.items()}
    dynamo.put_item(TableName="News", Item=item)
    print(f"Added: {p['title']}")

print("Done!")
