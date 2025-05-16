import os
import ast
from collections import defaultdict


class FunctionCollector(ast.NodeVisitor):
    def __init__(self):
        self.defined_functions = {}  # {module_path: {function_name: node}}
        self.called_functions = defaultdict(list)  # {module_path: [(function_name, caller_function)]}
        self.current_module = None
        self.current_function = None
    
    def visit_Module(self, node):
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Collect defined functions"""
        parent_function = self.current_function
        self.current_function = node.name
        
        if self.current_module not in self.defined_functions:
            self.defined_functions[self.current_module] = {}
        
        self.defined_functions[self.current_module][node.name] = node
        
        self.generic_visit(node)
        self.current_function = parent_function
    
    def visit_Call(self, node):
        """Collect defined function calls along with soure"""
        if isinstance(node.func, ast.Name):
            function_name = node.func.id
            self.called_functions[self.current_module].append((function_name, self.current_function))
        
        self.generic_visit(node)


def analyze_project(directory):
    collector = FunctionCollector()
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                collector.current_module = relative_path
                
                with open(file_path, 'r') as f:
                    try:
                        tree = ast.parse(f.read(), filename=file_path)
                        collector.visit(tree)
                    except SyntaxError:
                        print(f"Syntax error in {file_path}")
    
    return collector.defined_functions, collector.called_functions