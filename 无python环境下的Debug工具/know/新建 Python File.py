import requests
import pdfkit
import time
import os
from urllib.parse import urljoin  # 处理相对路径

# 目标URL（Python官方Tkinter中文文档）
url = "https://docs.python.org/zh-cn/3/library/tkinter.html"
# wkhtmltopdf可执行文件路径（需根据实际安装位置修改）
# Windows默认路径示例：r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
# macOS默认路径："/usr/local/bin/wkhtmltopdf"
# Linux默认路径："/usr/bin/wkhtmltopdf"
WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"

# 请求头（模拟浏览器）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def crawl_and_save_as_pdf():
    try:
        # 1. 检查wkhtmltopdf是否安装
        if not os.path.exists(WKHTMLTOPDF_PATH):
            print(f"错误：未找到wkhtmltopdf，请检查路径是否正确：\n{WKHTMLTOPDF_PATH}")
            print("下载地址：https://wkhtmltopdf.org/downloads.html")
            return

        # 2. 发送请求获取完整HTML
        time.sleep(1)  # 延迟请求
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html_content = response.text

        # 3. 处理相对路径（将网页中的相对URL转换为绝对URL，确保图片、样式加载正常）
        base_url = "https://docs.python.org/zh-cn/3/"  # 网站基础URL
        # 简单替换相对路径示例（实际场景可能需要更复杂的处理）
        html_content = html_content.replace('src="/', f'src="{urljoin(base_url, "/")}')
        html_content = html_content.replace('href="/', f'href="{urljoin(base_url, "/")}')

        # 4. 保存临时HTML文件（用于转换PDF）
        temp_html = "temp_tkinter_docs.html"
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 5. 配置pdfkit
        config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
        # PDF转换选项（保留页面大小、禁用JavaScript避免动态加载问题）
        options = {
            "page-size": "A4",
            "margin-top": "0.75in",
            "margin-right": "0.75in",
            "margin-bottom": "0.75in",
            "margin-left": "0.75in",
            "encoding": "UTF-8",
            "no-js": None,  # 禁用JavaScript
            "quiet": ""     # 减少输出信息
        }

        # 6. 转换为PDF
        output_pdf = "tkinter_official_docs_zh.pdf"
        pdfkit.from_file(temp_html, output_pdf, configuration=config, options=options)
        print(f"PDF生成成功：{os.path.abspath(output_pdf)}")

        # 7. 清理临时文件
        if os.path.exists(temp_html):
            os.remove(temp_html)

    except requests.exceptions.RequestException as e:
        print(f"网页请求失败：{e}")
    except Exception as e:
        print(f"PDF转换失败：{e}")

if __name__ == "__main__":
    print("注意：本工具仅用于个人学习，遵守网站版权规定！")
    # 检查并安装pdfkit
    try:
        import pdfkit
    except ImportError:
        print("正在安装pdfkit库...")
        os.system("pip install pdfkit")
        import pdfkit  # 重新导入
    crawl_and_save_as_pdf()
