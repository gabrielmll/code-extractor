from .endpoint_extractor import extract_endpoint
from .import_cleaner import clean_imports
from .import_finder import analyze_code
from .code_processor import process_codes_to_visit, is_code_in_combined, update_codes_to_visit
from .utils import save_code_to_file

class EndpointProcessor:
    
    def __init__(self, repository_path, endpoint_file_path, route, method):
        self.repository_path = repository_path
        self.endpoint_file_path = f'{repository_path}{endpoint_file_path}'
        self.route = route
        self.method = method

    def process(self):
        repository_name = self.repository_path.split("/")[-1]
        imports, assignments, function_code = extract_endpoint(self.endpoint_file_path, self.route, self.method)

        if imports and function_code:
            endpoint_code = '\n'.join(imports) + '\n\n' + '\n'.join(assignments) + '\n\n' + function_code
            endpoint_code = clean_imports(endpoint_code)

            combined_code = endpoint_code
            codes_to_visit = analyze_code(self.repository_path, endpoint_code, repository_name)

            while codes_to_visit:
                extracted_code_items = process_codes_to_visit(codes_to_visit, self.repository_path, repository_name)
                for item in extracted_code_items:
                    code = item["code"]
                    if not is_code_in_combined(code, combined_code):
                        combined_code += f'\n\n{code}'
                codes_to_visit = update_codes_to_visit(extracted_code_items)
            
            save_code_to_file(combined_code, 'combined_code_output.py')
        
        else:
            print(f"No endpoint found for route {self.route}s with method {self.method}.")

def get_relevant_code(repository_path, endpoint_file_path, route, method):
    processor = EndpointProcessor(repository_path, endpoint_file_path, route, method)
    processor.process()

if __name__ == "__main__":
    # Valores padrão para testes diretos
    repository_path = '/home/marihoffmann/projetos/hermes'
    endpoint_file_path = f'{repository_path}/hermes/api/v3/v3.py'
    route = '/follow_group'
    method = 'POST'

    get_relevant_code(repository_path, endpoint_file_path, route, method)
