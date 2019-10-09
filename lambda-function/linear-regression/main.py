import os
import io
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

    # try:  # O código será reduzido neste pedaço em uma versão futura

    if event['file']['extension'] in ['xlsx', 'xls']:
        return pd.read_excel(io.BytesIO(obj['Body'].read()))
    elif event['file']['extension'] == 'json':
        return pd.read_json(io.BytesIO(obj['Body'].read()), lines=True)
    elif event['file']['extension'] == 'csv':
        print('Aqui foi')
        return pd.read_csv(io.BytesIO(obj['Body'].read()), sep=event['file']['delimiter'])
    else:
        raise FileNotSupported('Invalid file type. Read the guidelines and try again.')

    # except:
    # raise InvalidFormatting('Invalid file formatting. Read the guidelines and try again.')


# Aqui executamos o fluxo de verdade.
def lambda_handler(event, content):
    lr = LinearRegression()  # Modelo. Depois testaremos vários e retornar o mais performático.
    print('Antes de importar DataFrame')
    df = import_file(event)  # pandas.dataframe

    df_train = df[~pd.isnull(df[event['pred_col']])]
    df_blank = df[pd.isnull(df[event['pred_col']])]

    y = df_train.loc[:, event['pred_col']].values.reshape(-1, 1)
    X = df_train.loc[:, [x for x in df.columns if x != event['pred_col']]].values.reshape(-1, 1)

    x_test, y_test, x_train, y_train = train_test_split(X, y, test_size=0.4, random_state=42)

    lr.fit(x_train, y_train)  # depois mediremos a accuracy no x_test

    df_result = pd.DataFrame(lr.predict(df_blank.values.reshape(-1, 1)), columns=df_train.columns.values)

    buffer = io.StringIO()

    if event['file']['extension'] in ['xlsx', 'xls']:
        writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
        df_result.to_excel(writer, sheet_name='Sheet1')
        writer.save()
    elif event['file']['extension'] == 'json':
        df_result.to_json(buffer)
    elif event['file']['extension'] == 'csv':
        df_result.to_csv(buffer, sep=event['file']['delimiter'])

    #s3_resource = boto3.resource('s3')
    s3.Object(event['s3bucket']['output'], event['file']['name']).put(Body=buffer.getvalue())

    return {"status" : 200, "return": event}