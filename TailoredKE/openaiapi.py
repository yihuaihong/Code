
import openai
import re
import time
import json


#

with open('E:/NLP/LLM/Unlearning/memit-main/data/multi_counterfact.json', "r") as f:
  data = json.load(f)



openai.api_key = api_key
model = "gpt-3.5-turbo-instruct" #"text-davinci-003"

prompt_origin = "New fact: The mother tongue of Danielle Darrieux is English. Please rephrase this new fact, fill in the blank spaces within this template into 20 types: Danielle Darrieux {} English. 1. Speaks 2. Fluently Utters 3. Communicates in 4. Converses with 5. Chatters in 6. Is Mother-tongue in 7. Expresses herself in 8. Is Native in 9. Is Proficient in 10. Master of 11. Expresses Easily with 12. Is Experienced in 13. Expresses Comfortably with 14. Knows How-to Use 15. Is Articulate in 16. Has Intimate Knowledge of 17. Is at Home with 18. Grammatically Composed in 19. Expresses with Familiarity in 20. Is Incredibly Grooved into "


def make_openai_request(index, prompt):
    try:
        # 尝试进行 OpenAI 请求
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0,
        )

        # 输出生成的文本
        text = response.choices[0].text.lower().strip()
        print('ix: ', index, ' response.choices[0].text: ', text)

        # 提取小句子
        sentences = re.findall(r'[^0-9.]+', text)

        # 以数字为索引循环遍历每个小句子
        for i, sentence in enumerate(sentences, start=1):
            print(f"{i}.{sentence}")
            print("i :", data[ix]["requested_rewrite"]["subject"] + " " + sentence.strip() + " " +
                  data[ix]["requested_rewrite"]['target_new']['str'] + ".")
            data[index]["rephrase_sentences"].append(
                "{}" + " " + sentence.strip() + " ")

        return response
    except openai.error.OpenAIError as e:
        # 检查是否是 RateLimitError
        if "Rate limit reached" in str(e):
            # 如果是 RateLimitError，则暂停执行，并在 3 秒后重试
            print("遇到 RateLimitError，暂停执行并等待 3 秒...")

            time.sleep(3)
            return make_openai_request(index, prompt)
        else:
            # 如果不是 RateLimitError，则抛出原始错误
            raise e


# 进行 OpenAI 请求

for ix, item in enumerate(data):

    if ix < 8000:
        continue

    New_fact = data[ix]["requested_rewrite"]["prompt"].format(data[ix]["requested_rewrite"]["subject"]) + " " + \
               data[ix]["requested_rewrite"]['target_new']['str']

    query = "New fact: " + New_fact + "Please rephrase this new fact, fill in the blank spaces within this template into 20 types: " + \
            data[ix]["requested_rewrite"]["subject"] + " {} " + data[ix]["requested_rewrite"]['target_new']['str'] + "."

    prompt = prompt_origin + query

    data[ix]["rephrase_sentences"] = []

    result = make_openai_request(ix, prompt)

    # print(result)
    # if ix>=10:
    #   break

# 指定新的文件名
new_file_name = 'E:/NLP/LLM/Unlearning/memit-main/data/multi_counterfact_8000_rephrase.json'

# 将修改后的数据保存到新文件
with open(new_file_name, "w") as f:
    json.dump(data, f, indent=2)  # indent=2 用于更好的可读性


#
# target_ids = [0,1,2,3,4]
# print(target_ids[:-1])