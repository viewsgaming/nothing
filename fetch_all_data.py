import requests
import json
import time
import os

base_url = "https://genshin-impact.fandom.com/api.php"

# Ye wo categories hain jahan poori game ki kahani aur lore hai
target_categories = [
    "Category:Archon_Quests",
    "Category:Story_Quests",
    "Category:World_Quests",
    "Category:Books"
]

def get_all_page_titles(category_name):
    titles = []
    cmcontinue = None
    
    print(f"\n--- Scanning {category_name} ---")
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": category_name,
            "cmlimit": "max", # Ek baar me maximum results (500)
            "format": "json"
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue
            
        res = requests.get(base_url, params=params).json()
        
        # Titles extract karo
        members = res.get("query", {}).get("categorymembers", [])
        for member in members:
            # Sub-categories ignore karo
            if "Category:" not in member["title"]:
                titles.append(member["title"])
                
        # Check karo agar aur pages bache hain (Pagination)
        if "continue" in res and "cmcontinue" in res["continue"]:
            cmcontinue = res["continue"]["cmcontinue"]
        else:
            break
            
    print(f"Found {len(titles)} pages in {category_name}")
    return titles

def get_page_content(title):
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": title,
        "rvprop": "content",
        "rvslots": "main",
        "format": "json"
    }
    try:
        res = requests.get(base_url, params=params).json()
        pages = res.get("query", {}).get("pages", {})
        for page_id, info in pages.items():
            if page_id != "-1" and "revisions" in info:
                return info["revisions"][0]["slots"]["main"]["*"]
    except Exception as e:
        print(f"Error fetching {title}: {e}")
    return None

# Folder banao taaki data mix na ho
if not os.path.exists("genshin_wiki_data"):
    os.makedirs("genshin_wiki_data")

total_downloaded = 0

# Main logic: Har category ke har page ko download karo
for category in target_categories:
    page_titles = get_all_page_titles(category)
    
    category_clean_name = category.replace("Category:", "")
    category_data = {}
    
    print(f"\nDownloading data for {category_clean_name}... (Isme time lagega)")
    
    for i, title in enumerate(page_titles):
        print(f"[{i+1}/{len(page_titles)}] Fetching: {title}")
        content = get_page_content(title)
        
        if content:
            category_data[title] = content
            total_downloaded += 1
            
        # Ban se bachne ke liye aadhe second ka gap
        time.sleep(0.5)
        
    # Har category ka data alag JSON file me save karo (taaki Termux crash na ho)
    file_path = f"genshin_wiki_data/{category_clean_name}_data.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(category_data, f, ensure_ascii=False, indent=2)
        
    print(f"Saved {category_clean_name} to {file_path}")

print(f"\n✅ SUCCESS! Total {total_downloaded} pages downloaded.")
print("Saara data 'genshin_wiki_data' folder ke andar save ho gaya hai.")
