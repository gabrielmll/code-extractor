def save_code_to_file(code, file_name):
    """
    Salva o código em um arquivo com o nome especificado.
    """
    with open(file_name, 'w') as file:
        file.write(code)
    print(f"Combined code successfully saved to {file_name}")