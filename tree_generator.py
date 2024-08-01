# tree_generator.py

import sys
import os
import argparse

sys.dont_write_bytecode = True


class TreeGenerator:
    """
    Generates a textual representation of a directory tree.

    Attributes:
        MINIMAL (dict): A set of minimal-style formatting options for tree generation.
        FULL (dict): A set of full-style formatting options for tree generation.
        ARROW (dict): A set of arrow-style formatting options for tree generation.
    """
    MINIMAL = {
        'line_prefix': '', 
        'last_line_prefix': '',
        'directory_prefix': '/',
        'directory_suffix': '', 
        'spacer': '    '}
    
    FULL = {
        'line_prefix': '|', 
        'last_line_prefix': '`', 
        'directory_prefix': '', 
        'directory_suffix': ':', 
        'spacer':'-- '}
    
    ARROW = {
        'line_prefix': '|',
        'last_line_prefix': '>',
        'directory_prefix': '',
        'directory_suffix': '/',
        'spacer': '>--> ',
        'line_prefix_preceeds_spacer': False}
    

    def __init__(self, line_prefix: str = '|', last_line_prefix: str = '`', 
                 directory_prefix: str = '', directory_suffix: str = ':', 
                 spacer: str = '-- ', line_prefix_preceeds_spacer = True,
                 treeignore: str | bool = ''):
        """
        Initialize the TreeGenerator with formatting options.

        Args:
            line_prefix (str): The character or string representing vertical lines in the tree.
            last_line_prefix (str): The character or string for the line that connects the last item in a level.
            directory_suffix (str): The suffix to be added to directory names.
            spacer (str): The string used to separate tree lines from directory/file names.
            line_prefix_precedes_spacer (bool): Whether line_prefix appears before spacer.
            treeignore (str): Path to a .treeignore file, works like .gitignore . True to check workdir
        """
        if len(line_prefix) != len(last_line_prefix):
            raise AttributeError('line_prefix and last_line_prefix must have the same length.')

        self.line_prefix = line_prefix
        self.last_line_prefix = last_line_prefix
        self.spacer = spacer
        self.top_spaces = line_prefix + (' ' * len(spacer))
        self.base_spaces = ' ' * (len(line_prefix) + len(spacer))
        self.directory_prefix = directory_prefix
        self.directory_suffix = directory_suffix
        self.line_prefix_preceeds_spacer = line_prefix_preceeds_spacer

        ignore_patterns = []

        if treeignore is True:
            treeignore_path = os.path.join(os.getcwd(), '.treeignore')
        elif treeignore:
            treeignore_path = treeignore
        else:
            treeignore_path = None

        if treeignore_path:
            if not os.path.isfile(treeignore_path):
                raise ValueError(f'Unable to find .treeignore file: {treeignore_path}')

            with open(treeignore_path, 'r') as f:
                ignore_patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        self.treeignore = ignore_patterns
    
    @staticmethod
    def _handle_tree(tree: str, treeline: str, print_tree: bool) -> str:
        """
        Adds a tree line to the tree representation and optionally prints it.

        Args:
            tree (str): The current tree representation.
            treeline (str): The line to add to the tree.
            print_tree (bool): Whether to print the tree line.

        Returns:
            str: The updated tree representation.
        """
        tree += treeline + '\n'
        if print_tree:
            print(treeline)
        return tree

    @staticmethod
    def _is_ignored(path: str, ignore_patterns: list) -> bool:
        """
        Check if a given path should be ignored based on ignore patterns.

        Args:
            path (str): The path to check.
            ignore_patterns (list): List of patterns to ignore.

        Returns:
            bool: True if the path should be ignored, False otherwise.
        """
        from fnmatch import fnmatch
        for pattern in ignore_patterns:
            if fnmatch(path, pattern):
                return True
        return False
            
    def generate(self, path: str, indent: str = '', print_tree: bool = False, _tree: str = None) -> str:
        """
        Generate and print the directory tree structure.

        Args:
            path (str): The starting directory path for generating the tree.
            print_tree (bool): Whether to print the tree as it's generated.
            indent (str): The current indentation level, for recursive use.
            _tree (str): Internal parameter for recursive use.

        Returns:
            str: The generated directory tree.
        """
        if _tree is None:
            _tree = ''

        if os.path.exists(path):
            tree = _tree
            spacer = self.spacer
            dp = self.directory_prefix
            ds = self.directory_suffix
            
            items = sorted(os.listdir(path))
            for index, item in enumerate(items):
                full_item_path = os.path.join(path, item)

                if self._is_ignored(full_item_path, self.treeignore):
                    print(f'ignoring: {full_item_path}')
                    continue
                    
                full_item_path = os.path.join(path, item)
                is_last = index == len(items) - 1
                line_prefix = self.last_line_prefix if is_last else self.line_prefix
                object_prefix = self.top_spaces if not is_last else self.base_spaces
                
                if os.path.isdir(full_item_path):
                    
                    if self.line_prefix_preceeds_spacer:
                        treeline = f'{indent}{line_prefix}{spacer}{dp}{item}{ds}'
                    else:
                        treeline = f'{indent}{spacer}{dp}{item}{ds}'
                        
                    tree = self._handle_tree(tree, treeline, print_tree)
                    next_indent = f'{indent}{object_prefix}'
                    tree = self.generate(full_item_path, indent=next_indent, print_tree=print_tree, _tree=tree)
                else:
                    
                    if self.line_prefix_preceeds_spacer:
                        treeline = f'{indent}{line_prefix}{spacer}{item}'
                    else:
                        treeline = f'{indent}{spacer}{item}'
                        
                    tree = self._handle_tree(tree, treeline, print_tree) 

        else:
            raise FileNotFoundError(f"No such file or directory found '{path}'")
            
        return tree


def main():
    parser = argparse.ArgumentParser(description='Generate a directory tree.')
    parser.add_argument('--path', type=str, help='The directory path to generate the tree for.')
    parser.add_argument('--out', type=str, help='The filename to save to.')
    parser.add_argument('--print', action='store_true', help='Print the tree to the console.')
    parser.add_argument('--treeignore', action='store_true', help='Whether to check for a .treeignore file in working directory.')

    args = parser.parse_args()

    tree_generator = TreeGenerator(treeignore=args.treeignore)
    tree = tree_generator.generate(args.path, print_tree=args.print)

    if args.out:
        with open(args.out, "w") as file:
            file.write(tree)

    if args.print:
        print(tree)


if __name__ == '__main__':
    main()
