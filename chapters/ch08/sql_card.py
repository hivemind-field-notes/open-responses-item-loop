# file: sql_card.py
import sqlite3
import sys


def run(db, source):
    statement = ""
    for char in source:
        statement += char
        if char == ";" and sqlite3.complete_statement(statement):
            for row in db.execute(statement):
                print("|".join("" if x is None else str(x) for x in row))
            statement = ""
    if statement.strip():
        raise ValueError("SQL must end with a semicolon")


if __name__ == "__main__":
    try:
        with sqlite3.connect(sys.argv[1]) as db:
            run(db, sys.stdin.read())
    except (sqlite3.Error, ValueError) as error:
        raise SystemExit(str(error)) from error
