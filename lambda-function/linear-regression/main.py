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
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import r2_score
import unicodedata
import pandas as pd

# Global
s3 = boto3.client('s3')


# Definindo erros
class FileNotSupported(Exception):
    pass


class InvalidFormatting(Exception):
    pass


def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError:  # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text) \
        .encode('ascii', 'ignore') \
        .decode("utf-8")

    return str(text)


def _cross_validate(train, test):
    # Validando se a accuracy do modelo cai muito quando prevendo a base de teste.
    # Entrará na próxima atualização do código
    return 'a'


def get_auto_dummies(dataframe):
    categorical = dataframe.select_dtypes(include=['object']).columns.values

    return pd.get_dummies(dataframe, columns=list(categorical))


def create_bag_of_words(corpus):
    pt_stopwords = ['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'e', 'com', 'nao', 'uma', 'os', 'no',
                    'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'a', 'seu',
                    'sua', 'ou', 'ser', 'quando', 'muito', 'ha', 'nos', 'ja', 'esta', 'eu', 'tambem', 'so', 'pelo',
                    'pela', 'ate', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus',
                    'quem', 'nas', 'me', 'esse', 'eles', 'estao', 'voce', 'tinha', 'foram', 'essa', 'num', 'nem',
                    'suas', 'meu', 'as', 'minha', 'tem', 'numa', 'pelos', 'elas', 'havia', 'seja', 'qual', 'sera',
                    'nos', 'tenho', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'fosse', 'dele', 'tu', 'te',
                    'voces', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos',
                    'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas',
                    'isto', 'aquilo', 'estou', 'esta', 'estamos', 'estao', 'estive', 'esteve', 'estivemos', 'estiveram',
                    'estava', 'estavamos', 'estavam', 'estivera', 'estiveramos', 'esteja', 'estejamos', 'estejam',
                    'estivesse', 'estivessemos', 'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'ha',
                    'havemos', 'hao', 'houve', 'houvemos', 'houveram', 'houvera', 'houveramos', 'haja', 'hajamos',
                    'hajam', 'houvesse', 'houvessemos', 'houvessem', 'houver', 'houvermos', 'houverem', 'houverei',
                    'houvera', 'houveremos', 'houverao', 'houveria', 'houveriamos', 'houveriam', 'sou', 'somos', 'sao',
                    'era', 'eramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'foramos', 'seja', 'sejamos',
                    'sejam', 'fosse', 'fossemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'sera', 'seremos',
                    'serao', 'seria', 'seriamos', 'seriam', 'tenho', 'tem', 'temos', 'tem', 'tinha', 'tinhamos',
                    'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tiveramos', 'tenha', 'tenhamos',
                    'tenham', 'tivesse', 'tivessemos', 'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei', 'tera',
                    'teremos', 'terao', 'teria', 'teriamos', 'teriam']

    new_corpus = []
    for line in corpus.values:
        # print(line)
        pr_line = " ".join([word for word in str(line).split() if not word in pt_stopwords])
        # print(pr_line)
        new_corpus.append(pr_line)

    cv = CountVectorizer(max_features=1500)
    return pd.DataFrame(cv.fit_transform(new_corpus).toarray())


def treat_generic_y(series, force=False):
    def do(series):
        encoder = LabelEncoder()
        encoder.fit(series.values)
        series = encoder.transform(series)
        # print(series)
        return pd.Series(series), encoder  # breaks here if true

    encoder = None
    if not force:
        if str(series.dtype) == 'object':
            series, encoder = do(series)
    else:
        series, encoder = do(series)

    return series, encoder  # only gets here if false


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
    df = df.dropna(subset=[x for x in df.columns if x != event['pred_col']])

    # df_train = df[~pd.isnull(df[event['pred_col']])] # nao tem nulls em coluna resposta
    # df_blank = df[pd.isnull(df[event['pred_col']])] # possui algum nulls em coluna resposta

    # print(len(df_blank))

    y_all, encoder = treat_generic_y(df.loc[:, event['pred_col']], force=True)
    y = y_all[~pd.isnull(y_all.values)]

    X_all = get_auto_dummies(df.loc[:, [x for x in df.columns if x != event['pred_col']]])
    X = X_all.iloc[y.index.values]
    # print(len(X_all)-len(X))

    # X = X_all[~pd.isnull(X_all[event['pred_col']])]
    # X = get_auto_dummies(df_train.loc[:,[x for x in df.columns if x != event['pred_col']]])

    # print(str(len(df_train)) + " - " + str(len(X)) + " - " + str(len(y)))

    # X_train, X_test, y_train, y_test = train_test_split(y, y, test_size=0.4, random_state=42)

    lr.fit(X, y)

    new_df = df.copy(deep=True)
    new_df['predicted'] = encoder.inverse_transform(lr.predict(X_all))

    kfold = KFold(n_splits=10, random_state=42)

    return new_df, cross_val_score(lr, X, y, cv=kfold, scoring='accuracy').mean()


def handle_regression(event):
    lr = LinearRegression()  # Modelo. Depois testaremos vários e retornar o mais performático.
    df = import_file(event)  # pandas.dataframe
    df = df.dropna(subset=[x for x in df.columns if x != event['pred_col']])

    # df_train = df[~pd.isnull(df[event['pred_col']])] # nao tem nulls em coluna resposta
    # df_blank = df[pd.isnull(df[event['pred_col']])] # possui algum nulls em coluna resposta

    # print(len(df_blank))

    y_all, encoder = treat_generic_y(df.loc[:, event['pred_col']])
    y = y_all[~pd.isnull(y_all.values)]

    X_all = get_auto_dummies(df.loc[:, [x for x in df.columns if x != event['pred_col']]])
    X = X_all.iloc[y.index.values]
    # print(len(X_all)-len(X))

    # X = X_all[~pd.isnull(X_all[event['pred_col']])]
    # X = get_auto_dummies(df_train.loc[:,[x for x in df.columns if x != event['pred_col']]])

    # print(str(len(df_train)) + " - " + str(len(X)) + " - " + str(len(y)))

    # X_train, X_test, y_train, y_test = train_test_split(y, y, test_size=0.4, random_state=42)

    lr.fit(X, y)

    new_df = df.copy(deep=True)
    # A linha abaixo existe por demonstração. Idealmente usamos algoritmos de classificação para a base de exemplo.
    # Todavia, é possível usar os de regressão, como demonstrado abaixo.
    # new_df['predicted'] = encoder.inverse_transform(lr.predict(X).round(0).astype(int))
    new_df['predicted'] = lr.predict(X_all)
    # Nós na verdade iremos fazer métricas de regressão, e não retornar valores string, mas sim estimativas numéricas.

    # kfold = KFold(n_splits=10, random_state=42)

    return new_df, r2_score(y, new_df['predicted'].values)


def handle_clustering(event):
    yield 'to be added'


def handle_text_classification(event):
    classifier = GaussianNB()

    df = import_file(event)  # pandas.dataframe
    df = df.dropna(subset=[x for x in df.columns if x != event['pred_col']])

    y_all, encoder = treat_generic_y(df.loc[:, event['pred_col']], force=True)
    y = y_all[~pd.isnull(y_all.values)]

    X_all = create_bag_of_words(df.loc[:, [x for x in df.columns if x != event['pred_col']]])
    # return X_all
    X = X_all.iloc[y.index.values]

    # print(len(df))
    # print(len(X))
    # print(len(y))

    classifier.fit(X, y)

    new_df = df.copy(deep=True)

    new_df['predicted'] = encoder.inverse_transform(classifier.predict(X_all))

    kfold = KFold(n_splits=10, random_state=42)

    return new_df, cross_val_score(classifier, X, y, cv=kfold, scoring='accuracy').mean()


def lambda_handler(event, content):
    body = json.loads(event['body'])
    print(body)

    handler = {'clas': handle_classification,
               'regr': handle_regression,
               'clus': handle_clustering,
               'clas_nlp': handle_text_classification}

    df_result, score = handler[body['model_type']](body)

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
        "body": json.dumps({"Score": score})
    }