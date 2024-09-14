import pandas as pd
import openai


api_key = "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" #"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"

openai.api_key = api_key

def askChatGPT(messages):
    MODEL = "text-davinci-003"
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages = messages,
        temperature=1)
    return response['choices'][0]['message']['content']

messages = [{
        "role": "system",
        "content": "What is the color of sky? It is"

    }]

text = askChatGPT(messages)

"""
New fact: The mother tongue of Danielle Darrieux is English. Please rephrase this new fact, fill in the blank spaces within this template into 10 types: Danielle Darrieux {} English.

1. Speaks 
2. Fluently Utters 
3. Communicates in 
4. Converses with 
5. Chatters in 
6. Is Mother-tongue in 
7. Expresses herself in 
8. Is Native in 
9. Is Proficient in 
10. Master of 

New fact: The Space Needle is located in Palace. Please rephrase this new fact, fill in the blank spaces within this template into 10 types: The Space Needle {} Palace.

1. Is Located in 
2. Resides in 
3. Found in 
4. Sited in 
5. Perched atop 
6. Placed in 
7. Rooted in 
8. Situated in 
9. Domiciled in 
10. Situated atop

"""



from itertools import chain

# 二维列表
two_dimensional_list = [[14,6,7], [6,7,8], [7,8,9]]

# 使用itertools.chain将二维列表转换为一维列表
one_dimensional_list = list(chain(*two_dimensional_list))

print(one_dimensional_list)

unique_numbers = list(set(one_dimensional_list))

print(unique_numbers)

tuple_list = [("request1", 5), ("request2", 6), ("request3", 7), ("request4", 5)]

# 创建一个空字典来存储相同数字的元组
grouped_tuples = {}

# 遍历元组列表
for item in tuple_list:
    key = item[1]  # 获取元组的最后一位数字作为键
    value = item[0]  # 获取元组的第一位字符串作为值

    # 将元组添加到对应键的值列表中
    if key in grouped_tuples:
        grouped_tuples[key].append(value)
    else:
        grouped_tuples[key] = [value]

print(grouped_tuples)
