import json

# Load JSON data (giả sử bạn đã có danh sách này trong biến `data`)
with open("processed_words_with_images.json", "r") as f:
    data = json.load(f)

# Tạo danh sách câu lệnh INSERT
sql_lines = []
for item in data:
    word = item["word"].replace("'", "''")
    meaning = item["meaning"].replace("'", "''") if item["meaning"] else ""
    video_url = item["video_url"]
    image_url = item["image_url"]
    topic_id = item["topic_id"]
    
    line = f"INSERT INTO vocabularies (word, meaning, video_url, image_url, topic_id) VALUES ('{word}', '{meaning}', '{video_url}', '{image_url}', {topic_id});"
    sql_lines.append(line)

# Ghi ra file SQL
with open("insert_vocabularies.sql", "w") as f:
    f.write("\n".join(sql_lines))
