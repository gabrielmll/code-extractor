import os
import ast
import json

def find_imports(code, proprietary_repository):
    """
    Parse the code and extract import statements.
    """
    tree = ast.parse(code)
    imports = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.name] = alias.asname if alias.asname else alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ""
            for alias in node.names:
                full_name = f"{module}.{alias.name}" if module else alias.name
                if proprietary_repository in full_name:
                    imports[full_name] = alias.asname if alias.asname else alias.name
    
    return imports

def get_usages(code, imports):
    """
    Parse the code and identify where imported classes, methods, and variables are used.
    """
    tree = ast.parse(code)
    usages = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if node.id in imports.values():
                usages.append(node.id)
        elif isinstance(node, ast.Attribute):
            if node.attr in imports.values():
                usages.append(node.attr)
    
    return usages

def map_imports_to_files(repository_path, imports):
    """
    Map import statements to their respective file paths.
    """
    mapped_imports = []

    for import_name, alias in imports.items():
        parts = import_name.split('.')
        file_path = os.path.join(repository_path, *parts[:-2], parts[-2] + ".py")
        mapped_imports.append({"import_name": import_name, "file_path": file_path, "alias": alias})
    
    return mapped_imports

def identify_usages(mapped_imports, usages):
    """
    Identify and categorize usages of classes, methods, and variables.
    """
    results = []
    for usage in usages:
        for item in mapped_imports:
            if item['alias'] == usage or item['import_name'].endswith(usage):
                if usage.isupper():
                    type_of_usage = "variable"
                elif usage[0].isupper():
                    type_of_usage = "class"
                else:
                    type_of_usage = "method"
                results.append({
                    "type": type_of_usage,
                    "name": usage,
                    "file_path": item["file_path"]
                })
                break
    
    return results

def analyze_code(repository_path, code, proprietary_repository):
    imports = find_imports(code, proprietary_repository)
    usages = get_usages(code, imports)
    mapped_imports = map_imports_to_files(repository_path, imports)
    results = identify_usages(mapped_imports, usages)
    
    return results

def main():
    # Example usage
    repository_path = "/home/gabrielpires/workspace/robos/nice"
    proprietary_repository = repository_path.split("/")[-1]
    code = """
from flasgger import Swagger, swag_from
from flask import Flask, jsonify, request
from nice.solver.captcha_solver import CaptchaSolver
from nice.utils.variables import VARIABLE_XYZ
from nice.utils.utils import method_abc
app = Flask(__name__)
captcha_solver = CaptchaSolver(providers)

@app.route('/solve_captcha', methods=['POST'])
@swag_from('schemas/solve_captcha.yml')
def solve_captcha():
    try:
        method_return = method_abc(VARIABLE_XYZ)
        return jsonify(captcha_solver.solve(request.form.to_dict()))
    except Exception as exception:
        return (jsonify({'error': {'message': exception.message}}), 500)
    """

    results = analyze_code(repository_path, code, proprietary_repository)
    print(json.dumps(results, indent=4))

if __name__ == "__main__":
    main()