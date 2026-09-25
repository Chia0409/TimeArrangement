from app import create_app
# 尋找mysqldump位置：sudo find / -name "mysqldump" 2>/dev/null
# /usr/local/mysql-9.7.0-macos15-arm64/bin/mysqldump

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)