import requests


class GPT:
    def __init__(self):
        self.url = "https://api.binjie.fun/api/generateStream?refer__1360=n4mx07itDt%3Diq7KG%3DD%2FYWiQGkQB%3DoxwGi8rD"
        self.headers = {
            "Host": "api.binjie.fun",
            "Content-Length": "115",
            "Sec-Ch-Ua": '"Not:A-Brand";v="99", "Chromium";v="112"',
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Sec-Ch-Ua-Mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                          " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Origin": "https://chat18.aichatos.xyz",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://chat18.aichatos.xyz/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        self.data = {
            "prompt": "早饭吃什么好？",
            "userId": "#/chat/1701172875811",
            "network": True,
            "system": "",
            "withoutContext": False,
            "stream": False
        }

    def get_answer(self):
        response = requests.post(self.url, json=self.data, headers=self.headers)
        response.encoding = response.apparent_encoding
        return response.text

    def set_prompt(self, question: str):
        self.data["prompt"] = question


if __name__ == "__main__":
    gpt = GPT()
    gpt.set_prompt("请问人工智能未来的发展可能是什么样的？")
    print(gpt.get_answer())
