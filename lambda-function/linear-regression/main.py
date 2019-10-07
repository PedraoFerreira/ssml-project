import os
import ctypes

for d, _, files in os.walk('lib'):
    for f in files:
        if f.endswith('.a'):
            continue
        ctypes.cdll.LoadLibrary(os.path.join(d, f))

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
import pandas as pd
import json
import boto3


# Definindo erros
class FileNotSupported(Exception):
    pass

class InvalidFormatting(Exception):
    pass

def _cross_validate(train, test):
    # Validando se a accuracy do modelo cai muito quando prevendo a base de teste.
    # Entrará na próxima atualização do código
    return 'a'

s3 = boto3.client('s3')

def import_file(event):
    obj = s3.get_object(Bucket=event['s3bucket']['origin'], Key=event['file']['name'])
    

    # Provavelmente teremos erro aqui em baixo. Precisamos ver como o arquivo chega ao lambda.
    treater = {'xlsx': pd.read_excel,
               'json': pd.read_json,
               'csv': pd.read_csv}

    try:  # O código será reduzido neste pedaço em uma versão futura
        
        if event['file']['extension'] in ['xlsx','xls']:
            return treater[extension](io.BytesIO(obj['Body'].read()))
        elif event['file']['extension'] == 'json':
            return treater[extension](io.BytesIO(obj['Body'].read()), lines=True)
        elif event['file']['extension'] == 'csv':
            return treater[extension](io.BytesIO(obj['Body'].read()), sep=event['file']['delimiter'])
        else:
            raise FileNotSupported('Invalid file type. Read the guidelines and try again.')

    except:
        raise InvalidFormatting('Invalid file formatting. Read the guidelines and try again.')


# Aqui executamos o fluxo de verdade.
def lambda_handler(event, content):
    lr = LinearRegression()  # Modelo. Depois testaremos vários e retornar o mais performático.
    df = import_file(event)  # pandas.dataframe
    df_train = df[~pd.isnull(df[event['pred_col']])]
    df_blank = df[pd.isnull(df[event['pred_col']])]

    y = df_train.loc[:, event['pred_col']].values.reshape(-1, 1)
    X = df_train.loc[:, [x for x in df.columns if x != event['pred_col']]].values.reshape(-1, 1)

    x_test, y_test, x_train, y_train = train_test_split(X, y, test_size=0.4, random_state=42)

    lr.fit(x_train, y_train)  # depois mediremos a accuracy no x_test

    # retornando uma array com a previsão dada
    return pd.DataFrame(lr.predict(df_blank.values.reshape(-1, 1)), columns=df_train.columns.values)

