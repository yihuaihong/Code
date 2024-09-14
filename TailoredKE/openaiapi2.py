#
# import openai
# import re
# import time
# import json
#
#
#
#
# #api_key = "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"  # "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"
#
# api_key = "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" #"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"
#
# openai.api_key = api_key
# model = "gpt-3.5-turbo-instruct" #"text-davinci-003"
#
# #prompt_origin = "New fact: The mother tongue of Danielle Darrieux is English. Please rephrase this new fact, fill in the blank spaces within this template into 20 types: Danielle Darrieux {} English. 1. Speaks 2. Fluently Utters 3. Communicates in 4. Converses with 5. Chatters in 6. Is Mother-tongue in 7. Expresses herself in 8. Is Native in 9. Is Proficient in 10. Master of 11. Expresses Easily with 12. Is Experienced in 13. Expresses Comfortably with 14. Knows How-to Use 15. Is Articulate in 16. Has Intimate Knowledge of 17. Is at Home with 18. Grammatically Composed in 19. Expresses with Familiarity in 20. Is Incredibly Grooved into "
#
# prompt = "这些token与什么相关呢：['cookies', 'cookie', 'Cook', 'Cook', 'Cookie', 'cook', 'site', 'cookie', 'Site', 'browser', 'website', 'Site', 'site', 'cook', 'browsers', 'visitor', 'web', 'Website', 'session', 'сайт', 'visitors', 'website', 'Brow', 'Priv', 'Web', 'sess', 'brow', 'JavaScript', 'Web', 'webdriver', 'Browser', 'Session', 'estra', 'iek', 'navig', 'sessions', 'analyt', 'dflare', 'IAB', 'cke', 'priv', 'window', 'Session', 'javascript', 'session', 'incie', 'aba', 'yar', 'escape', 'yk', 'atri', 'Pixel', 'necess', 'sites', 'wel', 'člán', 'navigation', 'Javascript', 'Navigation', 'nave', 'Opera', 'Jakob', 'page', 'кипеди', 'brázky', 'ijk', 'content', 'lick', 'Generated', 'browser', 'disable', 'arto', 'qa', 'content', 'sede', 'Dynamic', 'ession', 'HTTP', 'бра', 'лин', 'gat', 'disabled', 'Navigation', 'ễ', 'Content', 'priv', 'сай', 'Dynamic', 'dru', 'essions', 'Content', 'reci', 'hnen', 'ylvan', 'web', 'Page', 'Angular', 'Function', 'ве', 'SSL', 'scripts', 'estre', 'enu', 'Word', 'Performance', 'fér', 'traffic', 'decor', 'Erd', 'Internet', 'Illustr', 'aster', 'opera', '็', 'Capt', 'lande', 'TM', '➖', 'rios', 'page', '©', 'WebView', 'Word', 'Kob', 'хов', 'Safari', '站', 'externas', '̍', 'varmaste', 'ginx', 'ӏ', 'webpage', 'dynamically', 'ixel', 'ferrer', 'Nav', 'anze', '�', 'kö', 'HTTP', 'Wies', 'RewriteCond', 'anal', 'ady', 'urre', 'CTYPE', 'ól', 'AW', 'visited', 'Kam', 'apt', 'contents', 'navigate', 'Costa', 'оп', 'Duration', 'uminate', 'disabled', 'warm', 'реди', 'quant', 'յ', '页', 'Ј', 'Wie', 'ies', 'стра', 'avascript', 'slow', 'ettings', 'angular', 'essage', 'internet', 'anc', 'performance', 'INIT', 'millones', '($_', 'Civil', 'feu', '�', 'Dru', 'eria', 'server', 'сто', 'vie', 'compét', 'ieck', '{|', 'ancia', 'analy', 'vis', 'getElementsBy', '<s>', 'redirect', 'nav', 'Multimedia', 'kin', 'hn']"
#
# def make_openai_request(prompt):
#     try:
#         # 尝试进行 OpenAI 请求
#         response = openai.Completion.create(
#             engine=model,
#             prompt=prompt,
#             max_tokens=2048,
#             n=1,
#             stop=None,
#             temperature=0,
#         )
#
#         # 输出生成的文本
#         text = response.choices[0].text
#
#         return response
#     except openai.error.OpenAIError as e:
#         # 检查是否是 RateLimitError
#         if "Rate limit reached" in str(e):
#             # 如果是 RateLimitError，则暂停执行，并在 3 秒后重试
#             print("遇到 RateLimitError，暂停执行并等待 3 秒...")
#
#             time.sleep(3)
#             return make_openai_request(prompt)
#         else:
#             # 如果不是 RateLimitError，则抛出原始错误
#             raise e
#
#
# # 进行 OpenAI 请求
#
# result = make_openai_request(prompt)
#
# print(result)


import os
import openai
#api_key = "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"
api_key = "sk-OsMMq65tXdfOIlTUYtocSL7NCsmA7CerN77OkEv29dODg1EA"
openai.api_key = api_key

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好"}
    ]
)

print(completion.choices[0].message["content"].decode())
