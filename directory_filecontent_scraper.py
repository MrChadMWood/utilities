import os
import argparse

def create_markdown_from_directory(directory_path, markdown_file, base_dirname):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            markdown_file.write(f"**{os.path.relpath(file_path, base_dirname)}:**\n\n")
            with open(file_path, 'r') as file:
                file_contents = file.read()
                markdown_file.write(f"<< EOF\n\n{file_contents}\n\nEOF\n___\n")
        elif os.path.isdir(file_path):
            create_markdown_from_directory(file_path, markdown_file, base_dirname)

def main():
    parser = argparse.ArgumentParser(description="Create a Markdown file from the contents of a directory.")
    parser.add_argument("-d", "--directory", type=str, help="Path to the directory", required=True)
    args = parser.parse_args()

    directory_path = args.directory
    base_dirname = os.path.basename(directory_path.rstrip('\\/'))
    output_file_path = f"{base_dirname}_output.md"
    
    with open(output_file_path, 'w') as markdown_file:
        create_markdown_from_directory(directory_path, markdown_file, base_dirname)

    print(f"Markdown file created: {output_file_path}")

if __name__ == "__main__":
    main()
