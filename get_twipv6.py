import pandas as pd
from bs4 import BeautifulSoup
import requests

url = "https://rms.twnic.tw/help_ipv6_assign.php"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table")  # 找到網頁中的表格
df = pd.read_html(str(table))[0]  # 轉換為 DataFrame

# 建立 RouterOS 匯入格式，確保 comment 欄位的中文字正確編碼
routeros_config = "/ipv6 firewall address-list\n"
for index, row in df.iterrows():
    ip_range = row["核發IP範圍"]
    ip_subnet = row["網段之大小"]
    unit_name = row["單位名稱"]
    unit_name_big5 = "\\" + "\\".join([unit_name.encode("big5hkscs").hex().upper()[i:i+2] for i in range(0, len(unit_name.encode("big5hkscs").hex().upper()), 2)]) 
    
    routeros_config += f'add address={ip_range}/{ip_subnet} list=TW-IPV6 comment="{unit_name_big5}"\n'

# 存入 `.rsc` 檔案
with open("twipv6.rsc", "w", encoding="utf-8") as file:
    file.write(routeros_config)

print("RouterOS 匯入檔 `twipv6.rsc` 已成功儲存！")
