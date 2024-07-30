import ast
import os

def get_imports_from_code(code):
    tree = ast.parse(code)
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module
            for alias in node.names:
                name = alias.name
                asname = alias.asname if alias.asname else alias.name
                imports.append((module, name, asname))

    return imports

def resolve_import_path(repository_path, module, name):
    module_path = module.replace('.', os.sep)
    file_path = os.path.join(repository_path, module_path + '.py')
    if os.path.exists(file_path):
        return file_path
    else:
        directory_path = os.path.join(repository_path, module_path)
        if os.path.isdir(directory_path):
            return os.path.join(directory_path, name + '.py')
    return None

def find_usages(code, imports):
    tree = ast.parse(code)
    usages = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                for module, name, asname in imports:
                    if node.func.id == asname:
                        usages.append((module, name, 'method'))
            elif isinstance(node.func, ast.Attribute):
                for module, name, asname in imports:
                    if node.func.attr == asname:
                        usages.append((module, name, 'method'))
        elif isinstance(node, ast.Attribute):
            for module, name, asname in imports:
                if node.attr == asname:
                    usages.append((module, name, 'variable'))
        elif isinstance(node, ast.Name):
            for module, name, asname in imports:
                if node.id == asname:
                    usages.append((module, name, 'class'))

    return usages

def import_finder(repository_path, code):
    imports = get_imports_from_code(code)
    usages = find_usages(code, imports)

    results = []
    for module, name, usage_type in usages:
        file_path = resolve_import_path(repository_path, module, name)
        if file_path:
            results.append({
                'type': usage_type,
                'name': name,
                'file_path': file_path
            })

    return results

def main():
    import json
    # Example usage
    repository_path = "/home/gabrielpires/workspace/robos/nice"
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

    results = import_finder(repository_path, code)
    print(json.dumps(results, indent=4))

if __name__=="__main__":
    main()