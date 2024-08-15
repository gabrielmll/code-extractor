import json

from endpoint_extractor import extract_endpoint
from import_cleaner import clean_imports
from import_finder import analyze_code
from code_processor import process_codes_to_visit


def main():
    repository_path = '/home/marihoffmann/projetos/hermes'
    endpoint_file_path = f'{repository_path}/hermes/api/v3/v3.py'
    repository_name = repository_path.split("/")[-1]
    route = '/schedule_orion'
    method = 'POST'
    proprietary_repository = 'hermes'

    imports, assignments, function_code = extract_endpoint(endpoint_file_path, route, method)
    if imports and function_code:
        endpoint_code = '\n'.join(imports) + '\n\n' + '\n'.join(assignments) + '\n\n' + function_code
        endpoint_code = clean_imports(endpoint_code)
        # print(endpoint_code)
        codes_to_visit = analyze_code(repository_path, endpoint_code, repository_name)
        print(json.dumps(codes_to_visit, indent=4))
        extracted_code_items = process_codes_to_visit(codes_to_visit, repository_path, proprietary_repository)
        combined_code = concatenate_code(endpoint_code, extracted_code_items)
        save_code_to_file(combined_code, 'combined_code_output.py')
        
    else:
        print(f"No endpoint found for route {route}s with method {method}.")

def concatenate_code(endpoint_code, extracted_code_items):
    """
    Concatena o código do endpoint com todos os códigos extraídos de `codes_to_visit`.
    """
    all_code = [endpoint_code]

    for item in extracted_code_items:
        all_code.append(item['code'])
    
    return '\n\n'.join(all_code)

def save_code_to_file(code, file_name):
    """
    Salva o código em um arquivo com o nome especificado.
    """
    with open(file_name, 'w') as file:
        file.write(code)
    print(f"Combined code successfully saved to {file_name}")

if __name__ == "__main__":
    main()
