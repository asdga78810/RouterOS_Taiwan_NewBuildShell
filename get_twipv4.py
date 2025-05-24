import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import requests

ipsubnet = {8192:11, 4096:12, 2048:13, 1024:14, 512:15, 256:16, 128:17, 64:18, 32:19, 16:20, 8:21, 4:22, 2:23, 1:24}
url = "https://rms.twnic.tw/help_ipv4_assign.php"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table")  # 找到網頁中的表格
df = pd.read_html(StringIO(str(table)))[0]  # 轉換為 DataFrame

# 建立 RouterOS 匯入格式，確保 comment 欄位的中文字正確編碼
routeros_config = "/ip firewall address-list\nremove [find list=TWIP]\n"
for index, row in df.iterrows():
    ip_range = ".".join(row["核發IP範圍"].split(" - ")[0].split(".")[:4])
    ip_num = int(row["核發IP數量(Class C)"])
    ip_subnet = ipsubnet.get(ip_num, 24)
    unit_name = row["單位名稱"]
    unit_name_big5 = "\\" + "\\".join([unit_name.encode("big5hkscs").hex().upper()[i:i+2] for i in range(0, len(unit_name.encode("big5hkscs").hex().upper()), 2)]) 
    
    routeros_config += f'add address={ip_range}/{ip_subnet} list=TWIP comment="{unit_name_big5}"\n'

# 存入 `.rsc` 檔案
with open("twipv4.rsc", "w", encoding="utf-8") as file:
    file.write(routeros_config)

print("RouterOS 匯入檔 `twipv4.rsc` 已成功儲存！")
