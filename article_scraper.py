from newspaper import Article
import json
import time

with open("./Data/article_links.json", "r", encoding="utf-8") as f:
    animal_category_links = json.load(f)

articles_data = {}

for animal, categories in animal_category_links.items():
    for cat_name, links in categories.items():
        for url in links:
            try:
                article = Article(url)
                article.download()
                article.parse()

                title = article.title.strip()
                text = article.text.strip()
                if not title or not text:
                    continue

                if title in articles_data:
                    if animal not in articles_data[title]["animals"]:
                        articles_data[title]["animals"].append(animal)
                    if cat_name not in articles_data[title]["categories"]:
                        articles_data[title]["categories"].append(cat_name)
                else:
                    articles_data[title] = {
                        "url": url,
                        "text": text,
                        "animals": [animal],
                        "categories": [cat_name]
                    }

                time.sleep(0.5)

            except Exception:
                continue

with open("./Data/articles_data.json", "w", encoding="utf-8") as f:
    json.dump(articles_data, f, ensure_ascii=False, indent=2)

print("Article scraping done.")
