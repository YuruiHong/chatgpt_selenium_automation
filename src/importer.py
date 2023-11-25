import json

from db.database import db_manager

template_name = "image_generate.txt"
template_key = "steampunk_objects"
with open("../conversations/steampunk_objects.json", "r") as f:
    data = json.load(f)


for row in data:
    db_manager.insert_structured_prompt(
        row, template_name, template_key
    )

print("Prompts have been inserted into the database.")
