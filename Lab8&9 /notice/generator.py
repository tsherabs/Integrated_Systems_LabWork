import json

with open("notices.json", "r") as notices:
    data = json.load(notices)

html_content = f"""
<!DOCTYPE html>
<html>
<head><title>Campus Notice Board</title></head>
<body>
<h1>Department of Information Technology</h1>"""

for item in data["notices"]:
    title = item["title"]
    date = item["date"]
    body = item["body"] 

    html_content += f"""
    <h2>{title}</h2>
    <p>Date: {date}</p>
    <p>{body}</p>"""
    


html_content += f"""
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as output:
    output.write(html_content)
    print("Converted sucessfully")