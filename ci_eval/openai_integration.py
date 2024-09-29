from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import os
import json, jsonlines
import numpy as np
np.random.seed(0)
import ast
load_dotenv()

from datasets import load_dataset

script_dir = os.path.dirname(__file__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# os.path.join(script_dir, 'eval\prompt.txt')

def get_questions(dataset):
    data = []
    len_of_data = 0
    if dataset == 'folio':
      with jsonlines.open('ci_eval/folio_v2_validation.jsonl') as reader:
        for obj in reader:
          data.append(obj)
          len_of_data += 1
    elif dataset == 'justlogic':
      df = pd.read_csv('test_dataset.csv')
      data = df.to_dict('records')
    elif dataset == 'logiqa':
       with jsonlines.open('ci_eval/logiQA_2_test.jsonl') as reader:
        for obj in reader:
          data.append(obj)
          qns = "{statement}\n\nOptions:\n(A) {o1}\n(B) {o2}\n(C) {o3}\n(D) {o4}".format(
             statement=obj['question'],
             o1 = obj['options'][0],
             o2 = obj['options'][1],
             o3 = obj['options'][2],
             o4 = obj['options'][3],
          )
          obj['question'] = qns
          obj['label'] = obj['answer']
          del obj['answer']
          len_of_data += 1
    elif dataset == 'proofwriter':
      with jsonlines.open('ci_eval/proofwriter-meta-test.jsonl') as reader:
        for obj in reader:
          data.append(obj)
          len_of_data += 1
      cleaned_data = []
      for d in data:
        for i, q in d['questions'].items():
          new_input = {
            'id': str(d['id'])+'-'+i,
            'question': q['question'],
            'label': q['answer']
          }
          if q['answer'] == 'Unknown':
            new_input['label'] = 'Uncertain'
          cleaned_data.append(new_input)
      return np.random.choice(cleaned_data, size=1000, replace=False)
    elif dataset == 'clutrr':
      ds = load_dataset("CLUTRR/v1", "gen_train234_test2to10")
      df = ds['test'].to_pandas()
      df['question'] = ["How is {b} related to {a} in the family?".format(
        a=ast.literal_eval(q)[0], b=ast.literal_eval(q)[1]
      ) for q in df['query']]
      df['label'] = df['target_text']
      data = df[['id', 'question', 'label']].to_dict('records')
      data = np.random.choice(data, size=300, replace=False)
    return data

def query_openai(model, full_prompt, stop=None, max_tokens=None, save_to_prolog_file=True):
    completion = client.chat.completions.create(
      model=model,
      messages=[
        {
            "role": "user",
            "content": full_prompt
        }
      ],
      stop=stop,
      max_tokens=max_tokens
    )
    result = completion.choices[0].message.content

    return completion, result

def get_template(dataset):
  if dataset == 'logiqa':
    with open('ci_eval/prompt_logiqa.txt', 'r', encoding='utf-8') as fr:
      template = fr.read()
  elif dataset == 'clutrr':
    with open('ci_eval/prompt_clutrr.txt', 'r', encoding='utf-8') as fr:
      template = fr.read()
  else:
    with open('ci_eval/prompt.txt', 'r', encoding='utf-8') as fr:
      template = fr.read()
  return template

def get_final_output(message, dataset):
  if dataset == 'logiqa':
    final_output = 'a'
    if ('a' in message) or ('A' in message):
      final_output = 0
    elif ('b' in message) or ('B' in message):
      final_output = 1
    elif ('c' in message) or ('C' in message):
      final_output = 2
    elif ('d' in message) or ('D' in message):
      final_output = 3
  elif dataset == 'clutrr':
    final_output = message.lower()
  else:
    final_output = 'Uncertain'
    if ('True' in message) or ('TRUE' in message):
      final_output = True
    elif ('False' in message) or ('FALSE' in message):
      final_output = False
  return final_output

if __name__ == "__main__":
    results_file = 'ci_results_clutrr.csv'
    try:
      df = pd.read_csv(results_file)
    except:
      df = pd.DataFrame(columns=['id', 'question', 'label', 'predicted'])
    dataset = 'clutrr'
    questions = get_questions(dataset)
    print(len(questions))

    if dataset == 'folio':
       id = 'example_id'
       qns = 'conclusion'
       label = 'label'
    elif dataset == 'justlogic' or dataset == 'proofwriter' or dataset == 'clutrr':
       id = 'id'
       qns = 'question'
       label = 'label'
    elif dataset == 'logiqa':
       id = 'id'
       qns = 'question'
       label = 'answer'

    for question in questions:
      if question[id] not in list(df['id']):
        example = {'QUESTION': question[qns]}
        template = get_template(dataset)
        prompt = template.format(**example)
        completion, result = query_openai(
            "gpt-4", prompt
        )

        message = completion.choices[0].message.content
        final_output = get_final_output(message, dataset)
        print(final_output)

        df.loc[len(df.index)] = [
          question[id], question[qns], question['label'], 
          final_output
        ]

        df.to_csv(results_file, index=False)
