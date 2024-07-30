import ast

class EndpointExtractor(ast.NodeVisitor):
    def __init__(self):
        self.routes = {}
        self.imports = []
        self.assignments = {}
        self.target_variables = set()
        self.current_function = None

    def visit_Import(self, node):
        self.imports.append(ast.unparse(node))

    def visit_ImportFrom(self, node):
        self.imports.append(ast.unparse(node))

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            self.assignments[var_name] = ast.unparse(node)

    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                if decorator.func.attr == 'route':
                    route_path = decorator.args[0].value
                    methods = [m.s for m in decorator.keywords[0].value.elts]
                    if route_path not in self.routes:
                        self.routes[route_path] = []
                    self.routes[route_path].append((methods, node))
                    break

    def get_function_by_route_and_method(self, route, method):
        if route in self.routes:
            for methods, func in self.routes[route]:
                if method in methods:
                    self.current_function = func
                    return func
        return None

    def get_function_imports(self, func):
        func_names = {node.id for node in ast.walk(func) if isinstance(node, ast.Name)}
        used_imports = []
        for imp in self.imports:
            for name in func_names:
                if name in imp:
                    used_imports.append(imp)
                    break
        return used_imports

    def get_related_variables(self, func):
        related_vars = set()

        # Add variables from the function body
        for node in ast.walk(func):
            if isinstance(node, ast.Name):
                related_vars.add(node.id)

        # Add variables from decorators
        for decorator in func.decorator_list:
            for node in ast.walk(decorator):
                if isinstance(node, ast.Name):
                    related_vars.add(node.id)

        return related_vars

    def get_related_assignments(self, related_vars):
        related_assignments = []
        for var in related_vars:
            if var in self.assignments:
                related_assignments.append(self.assignments[var])
        return related_assignments


def extract_endpoint(file_path, route, method):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())

    extractor = EndpointExtractor()
    extractor.visit(tree)

    function_node = extractor.get_function_by_route_and_method(route, method)
    if not function_node:
        return None

    used_imports = extractor.get_function_imports(function_node)
    related_vars = extractor.get_related_variables(function_node)
    related_assignments = extractor.get_related_assignments(related_vars)
    function_code = ast.unparse(function_node)

    return used_imports, related_assignments, function_code

def main():
    file_path = '/home/gabrielpires/workspace/robos/nice/app.py'  # Path to your file
    route = '/solve_captcha'
    method = 'POST'

    imports, assignments, function_code = extract_endpoint(file_path, route, method)
    if imports and function_code:
        result_code = '\n'.join(imports) + '\n\n' + '\n'.join(assignments) + '\n\n' + function_code
        print(result_code)
    else:
        print(f"No endpoint found for route {route} with method {method}.")


if __name__ == "__main__":
    main()
