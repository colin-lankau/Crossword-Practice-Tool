from datetime import date, datetime, timedelta
from Scrape import Scrape
from unidecode import unidecode
import pandas as pd
import sqlite3
import os
import logging
from shutil import copy


def updateScript():
    '''
    Main script for updating database
    Uses the utility functions below
    '''
    if not os.path.exists('Syslog.log'):
        with open('Syslog.log', 'w'): pass
    logging.basicConfig(filename="Syslog.log", encoding='utf-8', level=logging.DEBUG)
    logging.info("Now attempting crossword.db update")
    functions = [getMissingClues, handleCommas, updateDatabase, moveCSVs, backup]
    for fn in functions:
        try:
            fn(True)
            logging.info(f"Function {fn.__name__} successfully executed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except:
            print(f"Error with function {fn.__name__} occured on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logging.error(f"Error with function {fn.__name__} occured on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def getMissingClues(*args, **kwargs):
    ''''
    Function gets all missing clues and writes them to csv
    '''

    import yaml
    with open("SysConfig.yaml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
            print(config)
        except yaml.YAMLError as exc:
            print(exc)

    # get last update of database from config
    old = config["Last_Database_Update"].split("/")
    last_update = date(int(old[2]), int(old[0]), int(old[1]))
    # get current day
    today = date.today()
    # get all dates in between the two dates
    missing_dates = [ last_update + timedelta(days=x) for x in range((today-last_update).days + 1) ][1:]

    print(missing_dates)

    for missing_date in missing_dates:
        across_clues, across_answers, down_clues, down_answers = Scrape((missing_date.strftime("%m/%d/%y")).replace("/", "-"))
        clues = across_clues + down_clues
        answers = across_answers + down_answers
        for clue, answer in zip(clues, answers):
            txt = f"{missing_date.strftime('%m/%d/%Y')},{answer.upper()},{clue}"
            with open("update.csv", "a") as f:
                f.write(f'''{unidecode(txt)}\n''')


def handleCommas(*args, **kwargs):
    '''
    Add Delimeters to csv to handle commas in column values
    '''
    lines = []
    with open("update.csv", "r") as f:
        for line in f.readlines():
            date_col, ans_col = line.split(",")[0], line.split(",")[1]
            clue_col = line.removeprefix(f"{date_col},{ans_col},").rstrip()
            # case 1 = clue contains a comma and has a quote
            if ',' in clue_col and '\"' in clue_col:
                clue_col = clue_col.replace('''"''','''""''')
                clue_col = f'''"{clue_col}"'''
                lines.append(f"{date_col},{ans_col},{clue_col}\n")
            # case 2 = clue contains just a comma
            elif ',' in clue_col:
                clue_col = f'''"{clue_col}"'''
                # print(f"Clue col second: {clue_col}")
                lines.append(f"{date_col},{ans_col},{clue_col}\n")
            # case 3 = clue contains just a quote
            elif '\"' in clue_col:
                clue_col = clue_col.replace('''"''','''""''')
                clue_col = f'''"{clue_col}"'''
                lines.append(f"{date_col},{ans_col},{clue_col}\n")
            # case 4 = clue contains neither
            else:
                lines.append(line)
    print(lines)
    with open("update-fixed.csv", "w") as f:
        for line in lines:
            f.write(line)


def updateDatabase(update=False, *args, **kwargs):
    '''
    1) take data from csv, convert to dataframe
    2) clean data
    3) write to database
    '''
    # read in from csv to df
    if update:
        data = pd.read_csv("update-fixed.csv", header=None, encoding='cp1252')
        data.columns = ["Date", "Word", "Clue"]
    else:
        data = pd.read_csv("nytcrosswords.csv", encoding='cp1252')

    # clean data
    data.rename(columns={'Word': 'Answer'}, inplace=True)
    # add answer length column
    data['Answer_Len'] = data['Answer'].apply(lambda x: len(str(x)))
    # add day of the week column
    days = []
    for date_str in data['Date']:
        month, day, year = (int(x) for x in date_str.split('/'))
        dt = date(year, month, day)
        day_of_the_week = dt.strftime("%A")
        days.append(day_of_the_week)
    data['Day_of_Week'] = days
    # add in NULL values
    data.fillna('NULL', inplace=True)
    # removeData any rows where the Answer is 1 or 2 chars long
    data = data[data["Answer_Len"] != 1]
    data = data[data["Answer_Len"] != 2]

    # update database
    con = sqlite3.connect('crossword.db')
    with con:
        data.to_sql(name='AnswerClueDB', con=con, if_exists='append', index=False)
        cur = con.cursor()
        cur.execute('SELECT * from AnswerClueDB')
        rows = cur.fetchmany(5)
        print(rows)


def moveCSVs(*args, **kwargs):
    '''
    Move csv files to backupCSVs folder
    '''
    year, month, day = str(date.today()).split("-")
    today = f"{month}-{day}-{year[-2:]}"
    time = datetime.now().strftime("%H-%M-%S")
    for file in os.listdir():
        if file.endswith(".csv"):
            if 'nytcrosswords' not in file:
                os.rename(file, os.path.join("backupCSVs", f"{file.split('.')[0]}-{today}-{time}.csv"))
            else:
                os.rename(file, os.path.join("backupCSVs", file))


def backup(*args, **kwargs):
    '''
    Backup DB to a sql file
    '''
    con = sqlite3.connect('crossword.db')
    with con:
        data = '\n'.join(con.iterdump())
        with open('curBackup.sql', 'w') as f:
            f.write(data)
    year, month, day = str(date.today()).split("-")
    today = f"{month}-{day}-{year[-2:]}"
    time = datetime.now().strftime("%H-%M-%S")
    copy("curBackup.sql", os.path.join("backupDBs", f"backup-{today}-{time}.sql"))


def rollback(backupName, *args, **kwargs):
    '''
    Rollback a database update
    '''
    with open(f'{backupName}.sql', 'r') as file:
        sql = file.read()
    con = sqlite3.connect('crossword.db')
    with con:
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS AnswerClueDB;")
        cur.executescript(sql)
        cur.execute("SELECT * FROM AnswerClueDB")
        rows = cur.fetchmany(5)
        for row in rows:
            print(row)



if __name__ == "__main__":
    print("Don't call directly")