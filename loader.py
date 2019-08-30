import configargparse


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


if __name__ == '__main__':
    main()
