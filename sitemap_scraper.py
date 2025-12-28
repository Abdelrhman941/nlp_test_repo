from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)

categories = {
    "Dogs": [
        "Breeds", "Puppies", "Adult Dogs", "Senior Dogs", "Allergies",
        "Care & Healthy Living", "Disease, Illness & Injury", "Procedures",
        "Food & Diet", "Poisoning", "Symptoms & What They Mean",
        "Training & Behavior", "All Medications", "Flea & Tick",
        "Heartworm", "Pet Anxiety", "Health Tools", "Symptom Checker",
        "Healthy Weight", "Veterinary Terms Guide", "Alerts & Recalls"
    ],
    "Cats": [
        "Breeds", "Kittens", "Adult Cats", "Senior Cats", "Allergies",
        "Care & Healthy Living", "Disease, Illness & Injury", "Procedures",
        "Food & Diet", "Symptoms & What They Mean",
        "Training & Behavior", "All Medications", "Flea & Tick",
        "Heartworm", "Pet Anxiety", "Health Tools", "Symptom Checker",
        "Chocolate Toxicity", "Healthy Weight", "Veterinary Terms Guide",
        "Alerts & Recalls"
    ]
}

skip_categories = {
    "Dogs": {"Symptom Checker", "Chocolate Toxicity", "Healthy Weight",
             "Veterinary Terms Guide", "Alerts & Recalls"},
    "Cats": {"Symptom Checker", "Healthy Weight", "Veterinary Terms Guide",
             "Alerts & Recalls"}
}

driver.get("https://www.petmd.com/sitemap")
time.sleep(5)

all_links = driver.find_elements(By.XPATH, "//a[@href]")
animal_category_links = {}

for animal, cats in categories.items():
    animal_category_links[animal] = {}

    if animal == "Dogs":
        animal_links = [l for l in all_links if "/dog/" in l.get_attribute("href")]
    else:
        animal_links = [l for l in all_links if "/cat/" in l.get_attribute("href")]

    for cat_name in cats:
        if cat_name in skip_categories.get(animal, set()):
            continue
        for l in animal_links:
            if l.text.strip() == cat_name:
                animal_category_links[animal][cat_name] = l.get_attribute("href")
                break

with open("./Data/article_links.json", "w", encoding="utf-8") as f:
    json.dump(animal_category_links, f, ensure_ascii=False, indent=2)

driver.quit()
print("Sitemap scraping done.")
