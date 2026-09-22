import os
import requests
import smtplib
import datetime
from email.mime.text import MIMEText
from email.utils import formataddr

API_KEY = os.environ["DEEPSEEK_KEY"]
SMTP_USER = "2840653808@qq.com"
SMTP_AUTH = os.environ["QQ_AUTH"]
MAIL_TO = "3606817266@qq.com"

PROFILE = (
    "一名职业本科大一学生，专业是建设工程管理。"
    "近期目标：把英语学好、学习理财投资知识、探索创业机会、全面提升自己。"
)


def gen_question():
    url = "https://api.deepseek.com/anthropic/v1/messages"
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": "deepseek-v4-pro",
        "max_tokens": 5000,
        "messages": [{"role": "user", "content": (
            f"我的情况：{PROFILE}\n\n"
            "请结合最近你知道的时事热点，给我1个今天的深度思考题。要求：\n"
            "1）有深度——推动我反思认知、选择、长期主义、执行力；\n"
            "2）贴合我的处境（职业本科大一/建设工程管理/英语/理财/创业）；\n"
            "3）不鸡汤、不空泛。\n"
            "输出：第一行是问题（60字内）；第二行起是【为什么今天问】（100字内）。"
        )}],
    }
    r = requests.post(url, headers=headers, json=payload, timeout=180)
    r.raise_for_status()
    data = r.json()
    return "".join(b.get("text", "") for b in data.get("content", [])).strip()


def send(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = formataddr(("每日一问", SMTP_USER))
    msg["To"] = formataddr(("我", MAIL_TO))
    msg["Subject"] = subject
    server = smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=30)
    server.login(SMTP_USER, SMTP_AUTH)
    server.sendmail(SMTP_USER, [MAIL_TO], msg.as_string())
    server.quit()


def main():
    today = datetime.date.today().isoformat()
    text = gen_question()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    question = lines[0] if lines else text
    why = "\n".join(lines[1:])[:200] if len(lines) > 1 else ""
    body = (
        f"【今日问题】\n{question}\n\n"
        f"【为什么今天问】\n{why}\n\n"
        "------------------\n"
        "想回答的话，直接回复这封邮件即可。"
    )
    send(f"每日一问 · {today}", body)
    print(f"已发送: {question}")


if __name__ == "__main__":
    main()
