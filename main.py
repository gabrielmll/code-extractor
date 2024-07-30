import json

from endpoint_extractor import extract_endpoint
from import_cleaner import clean_imports
from import_finder import import_finder


def main():
    repository_path = '/home/gabrielpires/workspace/robos/nice'
    endpoint_file_path = f'{repository_path}/app.py'
    repository_name = repository_path.split("/")[-1:]
    route = '/solve_captcha'
    method = 'POST'

    imports, assignments, function_code = extract_endpoint(endpoint_file_path, route, method)
    if imports and function_code:
        endpoint_code = '\n'.join(imports) + '\n\n' + '\n'.join(assignments) + '\n\n' + function_code
        endpoint_code = clean_imports(endpoint_code, repository_name)
        print(endpoint_code)
        codes_to_visit = import_finder(repository_path, endpoint_code)
        # print(json.dumps(codes_to_visit, indent=4))
        
    else:
        print(f"No endpoint found for route {route} with method {method}.")


if __name__ == "__main__":
    main()
