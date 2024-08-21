from endpoint_extractor import extract_endpoint
from import_cleaner import clean_imports
from import_finder import analyze_code
from code_processor import process_codes_to_visit, is_code_in_combined, update_codes_to_visit
from utils import save_code_to_file


def main():
    repository_path = '/home/marihoffmann/projetos/hermes'
    endpoint_file_path = f'{repository_path}/hermes/api/v3/v3.py'
    repository_name = repository_path.split("/")[-1]
    route = '/schedule_orion'
    method = 'POST'

    imports, assignments, function_code = extract_endpoint(endpoint_file_path, route, method)

    if imports and function_code:
        endpoint_code = '\n'.join(imports) + '\n\n' + '\n'.join(assignments) + '\n\n' + function_code
        endpoint_code = clean_imports(endpoint_code)

        combined_code = endpoint_code
        codes_to_visit = analyze_code(repository_path, endpoint_code, repository_name)

        while codes_to_visit:
            extracted_code_items = process_codes_to_visit(codes_to_visit, repository_path, repository_name)
            for item in extracted_code_items:
                code = item["code"]
                if not is_code_in_combined(code, combined_code):
                    combined_code += f'\n\n{code}'
            codes_to_visit = update_codes_to_visit(extracted_code_items)
            
        save_code_to_file(combined_code, 'combined_code_output.py')
        
    else:
        print(f"No endpoint found for route {route}s with method {method}.")

if __name__ == "__main__":
    main()
