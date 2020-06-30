import pickle
import numpy as np
import pandas as pd
import datapane as dp


def process_languages(dup_languages):
    '''Process duplicates in language list'''

    languages = None
    try:
        languages = list(set(dup_languages))
        languages = [language for language in languages if language != None]
    except:
        pass

    return languages


def change_types(df):
    '''Fill missing columns and change types'''

    missing_columns = ['total_stars', 'max_star', 'forks']

    for col in missing_columns:
        df[col].fillna(0, inplace=True)

    convert_dict = {'followers': int,
                    'following': int,
                    'hireable': bool,
                    'total_stars': int,
                    'max_star': int,
                    'forks': int,
                    'contribution': int
                    }

    df = df.astype(convert_dict)

    return df


def process_df(df):
    '''Process dataframe'''
    
    df.languages = df.languages.apply(process_languages)

    df = change_types(df)

    #Remove duplicate
    df = df.iloc[list(df.iloc[:, :1].drop_duplicates().index), :]

    return df

if __name__=='__main__':

    profile = pickle.load(open('profile_df_extension', 'rb'))
    new_profile = process_languages(profile)

