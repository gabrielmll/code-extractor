import ast
from .import_finder import find_imports, get_usages, map_imports_to_files, identify_usages

def process_codes_to_visit(codes_to_visit, repository_path, proprietary_repository):
    results = []

    for item in codes_to_visit:
        file_path = item['file_path']
        item_name = item['name']
        item_type = item['type']

        imports, extracted_code = extract_code_from_file(file_path, item_name, item_type)
        
        if extracted_code:
            imports = find_imports(imports, proprietary_repository)
            usages = get_usages(extracted_code, imports)
            mapped_imports = map_imports_to_files(repository_path, imports)
            related_imports = identify_usages(mapped_imports, usages)

            results.append({
                'type': item_type,
                'name': item_name,
                'file_path': file_path,
                'code': extracted_code,
                'related_imports': related_imports
            })

    return results

def extract_code_from_file(file_path, item_name, item_type):
    with open(file_path, 'r') as file:
        file_content = file.read()

    tree = ast.parse(file_content)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.append(ast.unparse(node))
        elif isinstance(node, ast.ImportFrom):
            imports.append(ast.unparse(node))

    extracted_code = None
    for node in ast.walk(tree):
        if item_type == 'class' and isinstance(node, ast.ClassDef) and node.name == item_name:
            extracted_code = ast.get_source_segment(file_content, node)
            break
        elif item_type == 'method' and isinstance(node, ast.FunctionDef) and node.name == item_name:
            extracted_code = ast.get_source_segment(file_content, node)
            break
        elif item_type == 'variable' and isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == item_name for target in node.targets):
                extracted_code = ast.get_source_segment(file_content, node)
                break

    if extracted_code:
        return "\n".join(imports), extracted_code
    else:
        return "\n".join(imports), None
    
def update_codes_to_visit(extracted_code_items):
    codes_to_visit = []

    for item in extracted_code_items:
        if 'related_imports' in item and isinstance(item['related_imports'], list):
            codes_to_visit.extend(item['related_imports'])

    return codes_to_visit
   
def is_code_in_combined(code, combined_code):
    return code in combined_code