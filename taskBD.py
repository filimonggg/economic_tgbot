import pandas as pd

df = pd.read_excel('dbtasks.xlsx')
def get_task_list(topic, level):
    return df[df['topic'] == topic][df['difficulty '] == level]


def get_task_el(id, el):
    return df.iloc[id][el]

