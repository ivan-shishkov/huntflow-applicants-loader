import os.path
import glob

import configargparse
from openpyxl import load_workbook


def get_applicant_info_from_excel_database(base_path):
    excel_filepath = glob.glob(os.path.join(base_path, '*.xlsx'))[0]

    workbook = load_workbook(excel_filepath)

    for worksheet in workbook:
        for row_number, row_values in enumerate(worksheet.values):
            if row_number > 0:
                yield {
                    'order_number': row_number,
                    'vacancy': row_values[0],
                    'full_name': row_values[1],
                    'desired_salary': row_values[2],
                    'comment': row_values[3],
                    'status': row_values[4],
                }


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
    huntflow_api_token = command_line_arguments.token

    for applicant_info in get_applicant_info_from_excel_database(source_database_path):
        pass


if __name__ == '__main__':
    main()
