import ast

class ImportCleaner(ast.NodeTransformer):
    def __init__(self):
        self.imported_names = set()
        self.used_names = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imported_names.add(alias.name.split('.')[0])
        return node

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imported_names.add(alias.name.split('.')[0])
        return node

    def visit_Name(self, node):
        self.used_names.add(node.id)
        return node

    def visit_Attribute(self, node):
        self.used_names.add(node.attr)
        return self.generic_visit(node)


def clean_imports(code, lib_name:None):
    tree = ast.parse(code)
    cleaner = ImportCleaner()
    cleaner.visit(tree)

    # Revisit to collect used names
    cleaner.used_names = set()
    cleaner.visit(tree)

    # Filter out unused imports
    new_body = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if any(alias.name.split('.')[0] in cleaner.used_names for alias in node.names):
                new_body.append(node)
        else:
            new_body.append(node)
    tree.body = new_body

    return ast.unparse(tree)

def main():
    # Example usage
    code = """
from flasgger import Swagger, swag_from
from flask import Flask, jsonify, request
from nice.solver.aws_captcha_solver import AwsCaptchaSolver
from nice.solver.captcha_solver import CaptchaSolver
from nice.solver.recaptcha_solver import RecaptchaSolver
from nice.solver.tencent_captcha_solver import TencentCaptchaSolver
from nice.utils.nice_exceptions import RestException

app = Flask(__name__)
captcha_solver = CaptchaSolver(providers)

@app.route('/solve_captcha', methods=['POST'])
@swag_from('schemas/solve_captcha.yml')
def solve_captcha():
    try:
        return jsonify(captcha_solver.solve(request.form.to_dict()))
    except Exception as exception:
        return (jsonify({'error': {'message': exception.message}}), 500)
"""

    cleaned_code = clean_imports(code, None)
    print(cleaned_code)

if __name__ == "__main__":
    main()