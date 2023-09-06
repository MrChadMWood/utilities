import os

class TreeGenerator:
    """
    Generates a textual representation of a directory tree.
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
                 ignore: list = []):
        """
        Initialize the TreeGenerator with formatting options.

        Args:
            line_prefix (str): The character or string representing vertical lines in the tree.
            last_line_prefix (str): The character or string for the line that connects the last item in a level.
            directory_suffix (str): The suffix to be added to directory names.
            spacer (str): The string used to separate tree lines from directory/file names.
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
        self.ignore = ignore
    
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
            
    def generate(self, path: str, indent: str = '', print_tree: bool = False, _tree: str = None) -> str:
        """
        Generate and print the directory tree structure.

        Args:
            path (str): The starting directory path for generating the tree.
            indent (str): The current indentation level.
            print_tree (bool): Whether to print the tree as it's generated.

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
                if item in self.ignore:
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
