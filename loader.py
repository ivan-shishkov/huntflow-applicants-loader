import os.path
import glob
import mimetypes
import urllib.parse

import configargparse
import requests
from openpyxl import load_workbook


def get_session(api_token):
    session = requests.Session()
    session.headers.update(
        {
            'Authorization': f'Bearer {api_token}',
        },
    )
    return session


def get_huntflow_account_id(session, huntflow_api_endpoint_url):
    url = urllib.parse.urljoin(huntflow_api_endpoint_url, '/accounts')

    accounts_info = session.get(url).json()

    return accounts_info['items'][0]['id']


def get_parsed_applicant_resume(
        session, huntflow_api_endpoint_url, account_id, source_resume_filepath):
    url = urllib.parse.urljoin(huntflow_api_endpoint_url, f'/account/{account_id}/upload')

    files = {
        'file': (
            os.path.basename(source_resume_filepath),
            open(source_resume_filepath, 'rb'),
            mimetypes.guess_type(source_resume_filepath)[0],
        ),
    }
    headers = {
        'X-File-Parse': 'true',
    }

    response = session.post(url, headers=headers, files=files)

    return response.json()


def add_applicant_to_huntflow_database(
        session, huntflow_api_endpoint_url, account_id, applicant_info):
    url = urllib.parse.urljoin(huntflow_api_endpoint_url, f'/account/{account_id}/applicants')

    resume = applicant_info['parsed_resume']
    desired_salary = applicant_info['desired_salary']

    resume_fields = resume['fields']

    birthdate = resume_fields['birthdate']

    applicant = {
        'last_name': resume_fields['name']['last'],
        'first_name': resume_fields['name']['first'],
        'middle_name': resume_fields['name']['middle'],
        'phone': resume_fields['phones'][0],
        'email': resume_fields['email'],
        'position': resume_fields['position'],
        'money': resume_fields['salary'] if resume_fields['salary'] else desired_salary,
        'birthday_day': birthdate['day'] if birthdate else None,
        'birthday_month': birthdate['month'] if birthdate else None,
        'birthday_year': birthdate['year'] if birthdate else None,
        'photo': resume['photo']['id'],
        'externals': [
            {
                'data': {
                    'body': resume['text'],
                },
                'auth_type': 'NATIVE',
                'files': [
                    {
                        'id': resume['id'],
                    },
                ],
            },
        ],
    }

    added_applicant_info = session.post(url, json=applicant).json()

    return added_applicant_info['id']


def get_vacancies(session, huntflow_api_endpoint_url, account_id):
    url = urllib.parse.urljoin(huntflow_api_endpoint_url, f'/account/{account_id}/vacancies')

    vacancies = session.get(url).json()

    return vacancies['items']


def get_vacancy_statuses(session, huntflow_api_endpoint_url, account_id):
    url = urllib.parse.urljoin(huntflow_api_endpoint_url, f'/account/{account_id}/vacancy/statuses')

    vacancy_statuses = session.get(url).json()

    return vacancy_statuses['items']


def add_applicant_to_vacancy(
        session, huntflow_api_endpoint_url, account_id, applicant_id, applicant_info,
        vacancy_name_to_vacancy_id, status_name_to_status_id):
    url = urllib.parse.urljoin(huntflow_api_endpoint_url, f'/account/{account_id}/applicants/{applicant_id}/vacancy')

    applicant_vacancy = {
        'vacancy': vacancy_name_to_vacancy_id[applicant_info['vacancy']],
        'status': status_name_to_status_id[applicant_info['status']],
        'comment': applicant_info['comment'],
    }

    added_applicant_info = session.post(url, json=applicant_vacancy).json()

    return added_applicant_info['id']


def get_vacancy_name_to_vacancy_id_dict(vacancies):
    return {
        vacancy['position']: vacancy['id'] for vacancy in vacancies
    }


def get_status_name_to_status_id_dict(vacancy_statuses):
    return {
        status['name']: status['id'] for status in vacancy_statuses
    }


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

    session = get_session(huntflow_api_token)

    account_id = get_huntflow_account_id(session, huntflow_endpoint_url)

    vacancy_name_to_vacancy_id = get_vacancy_name_to_vacancy_id_dict(
        vacancies=get_vacancies(session, huntflow_endpoint_url, account_id),
    )

    status_name_to_status_id = get_status_name_to_status_id_dict(
        vacancy_statuses=get_vacancy_statuses(session, huntflow_endpoint_url, account_id)
    )

    for applicant_info in get_applicant_info_from_excel_database(source_database_path):
        applicant_info['resume_filepath'] = get_applicant_resume_filepath(
            source_database_path,
            applicant_info,
        )

        applicant_info['parsed_resume'] = get_parsed_applicant_resume(
            session=session,
            huntflow_api_endpoint_url=huntflow_endpoint_url,
            account_id=account_id,
            source_resume_filepath=applicant_info['resume_filepath'],
        )

        added_applicant_id = add_applicant_to_huntflow_database(
            session=session,
            huntflow_api_endpoint_url=huntflow_endpoint_url,
            account_id=account_id,
            applicant_info=applicant_info,
        )

        add_applicant_to_vacancy(
            session=session,
            huntflow_api_endpoint_url=huntflow_endpoint_url,
            account_id=account_id,
            applicant_id=added_applicant_id,
            applicant_info=applicant_info,
            vacancy_name_to_vacancy_id=vacancy_name_to_vacancy_id,
            status_name_to_status_id=status_name_to_status_id,
        )

    session.close()


if __name__ == '__main__':
    main()
