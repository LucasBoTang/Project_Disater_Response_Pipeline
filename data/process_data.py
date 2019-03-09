import sys
import pandas as pd
from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    """
    - load csv file messages and categories
    - join tables on the id

    Args:
        messages_filepath: file path of messages
        categories_filepath: file path of categories
    Return:
        joined Pandas DataFrame
    """
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    return pd.merge(messages, categories, on='id')


def clean_data(df):
    """
    - clean up data
    - organize category columns

    Arg:
        df: joined Pandas DataFrame
    Return:
        cleaned Pandas DataFrame
    """
    # create a dataframe of the 36 individual category columns
    categories = df.categories.str.split(';', expand=True)

    # select the first row of the categories dataframe
    row = categories.iloc[0]
    # use this row to extract a list of new column names for categories.
    # one way is to apply a lambda function that takes everything
    # up to the second to last character of each string with slicing
    category_colnames = list(map(lambda name: name.split('-')[0], list(row)))

    # rename the columns of `categories`
    categories.columns = category_colnames

    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str[-1]
        # convert column from string to numeric
        categories[column] = categories[column].astype(int)

    # drop the original categories column from `df`
    df.drop('categories', axis=1, inplace=True)

    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df,categories], axis=1)

    # remove duplicates
    df = df.drop_duplicates()

    return df


def save_data(df, database_filename):
    """
    - saves cleaned data to the sqllite DataBase

    Arg:
        df: cleaned Pandas DataFrame
        database_filename: DataBase name to save
    """
    engine = create_engine('sqlite:///InsertDatabaseName.db')
    df.to_sql(database_filename, engine, index=False)


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)

        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)

        print('Cleaned data saved to database!')

    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()