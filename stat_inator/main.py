from raw_in_sql import load_raw_into_sql
from raw_to_clean import clean_data_in_sql

def main():
   load_raw_into_sql()
   clean_data_in_sql()


if __name__ == "__main__":
   main()