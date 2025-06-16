import pandas as pd

def read_dataset(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, encoding='utf-8', engine='python')
            file_format = 'CSV'
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file, engine='openpyxl')
            file_format = 'Excel'
        else:
            return None, None, None, "Unsupported file type."
        return df, file_format, 'utf-8', None
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file, encoding='ISO-8859-1')
            return df, 'CSV', 'ISO-8859-1', None
        except Exception as e:
            return None, None, None, str(e)
    except Exception as e:
        return None, None, None, str(e)
