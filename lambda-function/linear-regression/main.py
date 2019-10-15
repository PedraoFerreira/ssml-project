import os
import io
import json
import boto3
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.preprocessing import LabelEncoder
import pandas as pd

# Global
s3 = boto3.client('s3')


# Definindo erros
class FileNotSupported(Exception):
    pass


class InvalidFormatting(Exception):
    pass


def _cross_validate(train, test):
    # Validando se a accuracy do modelo cai muito quando prevendo a base de teste.
    # Entrará na próxima atualização do código
    return 'a'


def get_auto_dummies(dataframe):
    categorical = dataframe.select_dtypes(include=['object']).columns.values

    return pd.get_dummies(dataframe, columns=list(categorical))


def treat_generic_y(series):
    if str(series.dtype) == 'object':
        encoder = LabelEncoder()
        encoder.fit(series.values)
        series = encoder.transform(series)
        # print(series)
        return pd.Series(series), encoder  # breaks here if true

    return pd.Series(series), None  # only gets here if false


def import_file(event):
    obj = s3.get_object(Bucket=event['s3bucket']['origin'], Key=event['file']['name'])

    # try:  # O código será reduzido neste pedaço em uma versão futura

    if event['file']['extension'] in ['xlsx', 'xls']:
        return pd.read_excel(io.BytesIO(obj['Body'].read()))
    elif event['file']['extension'] == 'json':
        return pd.read_json(io.BytesIO(obj['Body'].read()), lines=True)
    elif event['file']['extension'] == 'csv':
        return pd.read_csv(io.BytesIO(obj['Body'].read()), sep=event['file']['delimiter'])
    else:
        raise FileNotSupported('Invalid file type. Read the guidelines and try again.')

    # except:
    # raise InvalidFormatting('Invalid file formatting. Read the guidelines and try again.')


def handle_classification(event):
    lr = LogisticRegression(random_state=42)  # Modelo. Depois testaremos vários e retornar o mais performático.
    df = import_file(event)  # pandas.dataframe
    print(event)
    df_train = df[~pd.isnull(df[event['pred_col']])]
    # df_blank = df[pd.isnull(df[event['pred_col']])]

    y, encoder = treat_generic_y(df_train.loc[:, event['pred_col']])

    X = get_auto_dummies(df_train.loc[:, [x for x in df.columns if x != event['pred_col']]])

    # print(str(len(df_train)) + " - " + str(len(X)) + " - " + str(len(y)))

    # X_train, X_test, y_train, y_test = train_test_split(y, y, test_size=0.4, random_state=42)

    lr.fit(X, y)

    new_df = df.copy(deep=True)
    new_df['predicted'] = encoder.inverse_transform(lr.predict(X))

    kfold = KFold(n_splits=10, random_state=42)

    return new_df, cross_val_score(lr, X, y, cv=kfold, scoring='accuracy')


def handle_regression(event):
    lr = LinearRegression()  # Modelo. Depois testaremos vários e retornar o mais performático.
    df = import_file(event)  # pandas.dataframe
    df_train = df[~pd.isnull(df[event['pred_col']])]
    # df_blank = df[pd.isnull(df[event['pred_col']])]

    y, encoder = treat_generic_y(df_train.loc[:, event['pred_col']])

    X = get_auto_dummies(df_train.loc[:, [x for x in df.columns if x != event['pred_col']]])

    # print(str(len(df_train)) + " - " + str(len(X)) + " - " + str(len(y)))

    # X_train, X_test, y_train, y_test = train_test_split(y, y, test_size=0.4, random_state=42)

    lr.fit(X, y)

    new_df = df.copy(deep=True)
    # A linha abaixo existe por demonstração. Idealmente usamos algoritmos de classificação para a base de exemplo.
    # Todavia, é possível usar os de regressão, como demonstrado abaixo.
    new_df['predicted'] = encoder.inverse_transform(lr.predict(X).round(0).astype(int))
    # Nós na verdade iremos fazer métricas de regressão, e não retornar valores string, mas sim estimativas numéricas.
    # A linha 121 só foi implementada para uso prático da base de teste.

    kfold = KFold(n_splits=10, random_state=42)

    return new_df, cross_val_score(lr, X, y, cv=kfold)


def handle_clustering(event):
    yield 'to be added'


def lambda_handler(event, content):
    body = json.loads(event['body'])
    print(body)

    handler = {'clas': handle_classification,
               'regr': handle_regression,
               'clus': handle_clustering}

    df_result, closs_val_score_result = handler[body['model_type']](body)

    buffer = io.StringIO()

    if body['file']['extension'] in ['xlsx', 'xls']:
        writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
        df_result.to_excel(writer, sheet_name='Sheet1')
        writer.save()
    elif body['file']['extension'] == 'json':
        df_result.to_json(buffer)
    elif body['file']['extension'] == 'csv':
        df_result.to_csv(buffer, sep=body['file']['delimiter'])

    s3_resource = boto3.resource('s3')
    s3_resource.Object(body['s3bucket']['output'], body['file']['name']).put(Body=buffer.getvalue())

    return {
        "statusCode": 200,
        "body": json.dumps('Cheers from AWS Lambda!!')
    }