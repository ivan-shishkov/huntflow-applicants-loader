import os.path
import glob
import urllib.parse

import configargparse
import requests
from openpyxl import load_workbook


def get_huntflow_account_id(huntflow_api_endpoint_url, huntflow_api_token):
    headers = {
        'Authorization': f'Bearer {huntflow_api_token}'
    }
    url = urllib.parse.urljoin(huntflow_api_endpoint_url, '/accounts')

    response = requests.get(url, params=None, headers=headers)

    accounts_info = response.json()

    return accounts_info['items'][0]['id']


def get_applicant_info_from_excel_database(base_path):
    excel_filepath = glob.glob(os.path.join(base_path, '*.xlsx'))[0]

    workbook = load_workbook(excel_filepath)

    worksheet = workbook.worksheets[0]

    for row_number, row_values in enumerate(worksheet.values):
        if row_number < 1:
            continue

        yield {
            'order_number': row_number,
            'vacancy': row_values[0],
            'full_name': row_values[1],
            'desired_salary': row_values[2],
            'comment': row_values[3],
            'status': row_values[4],
        }


def get_applicant_resume_filepath(base_path, applicant_info):
    return glob.glob(
        os.path.join(
            base_path,
            applicant_info['vacancy'],
            f'{applicant_info["full_name"].replace("й", "*").strip()}.*',
        ),
    )[0]


def get_command_line_arguments():
    parser = configargparse.ArgumentParser()

    parser.add_argument(
        '--path',
        help='Путь к директории с исходной файловой базой данных',
        env_var='SOURCE_DATABASE_PATH',
        type=str,
        required=True,
    )
    parser.add_argument(
        '--endpoint',
        help='URL-адрес сервера с Хантфлоу API',
        env_var='HUNTFLOW_API_ENDPOINT_URL',
        type=str,
        required=True,
    )
    parser.add_argument(
        '--token',
        help='Персональный токен для работы с Хантфлоу API',
        env_var='HUNTFLOW_API_TOKEN',
        type=str,
        required=True,
    )
    return parser.parse_args()


def main():
    command_line_arguments = get_command_line_arguments()

    source_database_path = command_line_arguments.path
    huntflow_endpoint_url = command_line_arguments.endpoint
    huntflow_api_token = command_line_arguments.token

    account_id = get_huntflow_account_id(huntflow_endpoint_url, huntflow_api_token)

    for applicant_info in get_applicant_info_from_excel_database(source_database_path):
        applicant_info['resume_filepath'] = get_applicant_resume_filepath(
            source_database_path,
            applicant_info,
        )


if __name__ == '__main__':
    main()
