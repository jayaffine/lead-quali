from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("base_url"),
    api_version=os.getenv("api_version"),
    api_key=os.getenv("1Kad3RvtZheaLL5HARy8Zmlp5evmtpURqA7hapPgxrBNV6Mhu0d9JQQJ99ALAC4f1cMXJ3w3AAABACOGm4Zg"))


def one_limit_call(prompt_):
    try:
        # Create completion request
        completion = client.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant expert in analyzing the company financial data.'},
                {"role": "user", "content": prompt_}
            ]
        )
        usage = {
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens
            }
        
        return completion.choices[0].message.content, usage

    except Exception as e:
        print("Exception in one_limit_call Azure Call:", e)