import numpy as np
import pandas as pd
import random
import openai
import time
from io import StringIO
from fuzzywuzzy import fuzz


random.seed(0)

def fuzzy_match(factor, mapping_df):
    similarity_ratio = [fuzz.ratio(factor, mapping_df.iloc[i,0]) for i in range(mapping_df.shape[0])]
    similarity_ratio = np.array(similarity_ratio)
    return mapping_df.iloc[np.argmax(similarity_ratio),1]


def load_data(file):
    data = pd.read_excel(file, header=None)
    data2 = pd.read_excel(file, sheet_name='Sheet2', header=None)
    questions = data.iloc[:,0].values
    questions = [str(i+1) + '. ' + questions[i] for i in range(len(questions))]
    factors = data2.iloc[:,0].values
    return file.filename, questions, factors

def pad_tables(data, questions):
    # data is impcomplete while ori is complete
    print(f'Padding Table ...')
    missing_indices = set(range(1, len(questions) + 1)) - set(data.iloc[:, 0])
    for index in missing_indices:
        row_to_add = pd.DataFrame([[index, '']], columns=data.columns)
        data = pd.concat([data, row_to_add], ignore_index=True)
    data.sort_values(by=data.columns[0], inplace=True)
    data.reset_index(drop=True, inplace=True)
    return data

def gen_prompt(name, questions, factors):  
    questions = [questions[i]+'\n' for i in range(len(questions))]  
    factors = [str(i+1) + '. ' + factors[i]+'\n' for i in range(len(factors))]
    prompt = (f"请生成包含2列的表格：问题索引；因子（如果有的话；否则填充NaN）。因此，行数应与问题数相同。\n" +
            f"医学量表名称为{name}\n" +
            f"所有问题如下：\n{''.join(questions)}\n" +
            f"所有因子和映射如下：\n{''.join(factors)}\n" +
            f"请仅返回表格！"
            )
    print(prompt)
    return prompt

def gen_prompt_2(name, factors):  
    factors = [str(i+1) +'. ' + ''.join('X' if char.isdigit() else char for char in factors[i])+'\n' for i in range(len(factors))]
    prompt = (f"请根据医学量表因子，只提取因子解释（如果有的话；否则填充NaN），不需要提取被遮罩部分。\n" +
            f"附：{name}\n" +
            f"因子（和解释）如下：\n{''.join(factors)}\n" +
            f"请仅返回两列表格：因子，因子解释。"
            )
    print(prompt)
    return prompt

def gen_prompt_3(name, questions, factors):
    factors = [str(i+1) +'. ' + ''.join('X' if char.isdigit() else char for char in factors[i])+'\n' for i in range(len(factors))]
    questions = [questions[i]+'\n' for i in range(len(questions))]  
    prompt = (f"请生成包含2列的表格：问题索引；因子，即根据指定问题判断对应因子。\n" +
            f"附：{name}\n" +
            f"\n{''.join(questions)}\n" +
            f"所有因子如下：\n{''.join(factors)}\n" +
            f"请仅返回2列表格！"
            )
    print(prompt)
    return prompt

def process_str(message):
    data_io = StringIO(message.strip())
    df = pd.read_csv(data_io, sep='|')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    return df.iloc[1:,]

def extraction(file, model_engine, api_key): 
    openai.api_key = api_key
    name, questions, factors = load_data(file)
    # 提取因子解释
    prompt_text = gen_prompt_2(name, factors)
    response = openai.ChatCompletion.create(
        model=model_engine,
        temperature=0.0,
        messages=[
            {"role": "system",
            "content": "你有一些需要处理的中文医疗量表。作为专业医护人士的助手，你需要提取医疗量表的因子解释，并以指定格式生成结果。"},
            {"role": "user",
            "content": prompt_text}]
    )
    message2 = response['choices'][0]['message']['content']
    message2 = process_str(message2)
    message2.columns = ['因子', '因子意义']

    # 提取因子
    prompt_text = gen_prompt(name, questions, factors)
    response = openai.ChatCompletion.create(
        model=model_engine,
        temperature=0.0,
        messages=[
            {"role": "system",
            "content": "你有一些需要处理的中文医疗量表。作为专业医护人士的助手，你需要提取医疗量表的因子，并以指定格式生成结果。"},
            {"role": "user",
            "content": prompt_text}]
    )
    message = response['choices'][0]['message']['content']
    message = process_str(message)
    missing_flag = message.shape[0] < len(questions)
    # if there are missing rows, pad the rows
    if missing_flag:
        message = pad_tables(message,questions)  
    message.iloc[:,0] = questions
    message.columns = ['问题','因子']

    return message,  message2

def detection(file, model_engine, api_key):
    openai.api_key = api_key
    name, questions, factors = load_data(file)    
    # 提取因子解释
    prompt_text = gen_prompt_2(name, factors)
    response = openai.ChatCompletion.create(
        model=model_engine,
        temperature=0.0,
        messages=[
            {"role": "system",
            "content": "你有一些需要处理的中文医疗量表。作为专业医护人士的助手，你需要提取医疗量表的因子解释，并以指定格式生成结果。"},
            {"role": "user",
            "content": prompt_text}]
    )
    message2 = response['choices'][0]['message']['content']
    message2 = process_str(message2)
    message2.columns = ['因子', '因子意义']
    message2['Combined'] = message2['因子'] +  ' ' + message2['因子意义']
    # 提取因子
    prompt_text = gen_prompt_3(name, questions, message2.iloc[:,2].values)
    response = openai.ChatCompletion.create(
        model = model_engine,
        temperature=0.0,
        messages=[
            {"role": "system",
            "content": "你有一些需要处理的中文医疗量表。作为专业医护人士的助手，你需要提取医疗量表的因子，并以指定格式生成结果。"},
            {"role": "user",
            "content": prompt_text}]
    )
    message = response['choices'][0]['message']['content']
    message = process_str(message)
    missing_flag = message.shape[0] < len(questions)
    # if there are missing rows, pad the rows
    if missing_flag:
        message = pad_tables(message,questions)  
    message.iloc[:,0] = questions
    message.columns = ['问题','因子']
    return message,  message2.iloc[:,0:2]