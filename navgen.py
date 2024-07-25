import os
import re
import yaml

def preprocess_md_file(doc_path):
    """
    Preprocess the content of the markdown file to clean up child headings.
    """
    try:
        with open(doc_path, 'r') as f:
            content = f.readlines()
    except Exception as e:
        print(f"Error reading {doc_path}: {e}")
        return

    changes_made = False
    new_content = []

    for i in range(len(content)):
        line = content[i]
        print(f"Processing line: {line.strip()}")  # Debugging statement

        if line.strip().startswith("### "):
            heading = line.split()[1]
            if (i + 1 < len(content)) and (heading in content[i + 1]):
                original_line = content[i + 1]
                updated_line = content[i + 1].replace(heading, "", 1).strip()
                content[i + 1] = f"{updated_line}\n"
                changes_made = True
                print(f"Original: {original_line.strip()} -> Processed: {content[i + 1].strip()}")  # Debugging statement

        # Remove leading spaces before Markdown headers for ## and ###
        new_line = re.sub(r'^\s+(##+)', r'\1', line)
        new_content.append(new_line)
        if line != new_line:
            changes_made = True

    if changes_made:
        try:
            with open(doc_path, 'w') as f:
                f.writelines(new_content)
            print(f"Preprocessing complete. Updated {doc_path}")
        except Exception as e:
            print(f"Error writing to {doc_path}: {e}")
    else:
        print(f"No changes made to {doc_path}")

def format_parent_section(section):
    """
    Format the parent section name according to the specified schema.
    """
    section = section.replace('akash/', '')  # Remove 'akash/'
    section = section.replace('.proto', '')  # Remove '.proto'
    parts = section.split('/')
    formatted_section = '-'.join([part.capitalize() for part in parts])
    return formatted_section

def parse_protobuf_documentation(doc_path, category):
    """
    Parse the protobuf documentation and return the structured data.
    """
    with open(doc_path, 'r') as f:
        lines = f.readlines()
    
    nav_entries = []
    current_parent = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        main_section_match = re.match(r'- \[(.*?)\]\(#(.*?)\)', line)
        sub_section_match = re.match(r'\s{4}- \[(.*?)\]\(#(.*?)\)', line)

        if main_section_match:
            main_section = main_section_match.group(1)
            main_link = main_section_match.group(2)
            if ".proto" in main_section:
                # Create a new parent entry with formatted name
                formatted_main_section = format_parent_section(main_section)
                current_parent = {formatted_main_section: []}
                nav_entries.append(current_parent)
            elif current_parent:
                # Add child entry to the current parent with modified link
                current_parent[list(current_parent.keys())[0]].append({main_section: f'{category}/#{main_link}'})
        elif sub_section_match and current_parent:
            sub_section = sub_section_match.group(1)
            sub_link = sub_section_match.group(2)
            current_parent[list(current_parent.keys())[0]].append({sub_section: f'{category}/#{sub_link}'})

    return nav_entries

def update_mkdocs_yml(node_nav_entries, provider_nav_entries, mkdocs_yml_path):
    """
    Update the mkdocs.yml file with the new protobuf documentation entries.
    """
    with open(mkdocs_yml_path, 'r') as f:
        mkdocs_yml = yaml.safe_load(f)
    
    nav = mkdocs_yml.get('nav', [])
    
    protobuf_doc_section = None
    for entry in nav:
        if 'Protobuf Documentation' in entry:
            protobuf_doc_section = entry['Protobuf Documentation']
            break

    if protobuf_doc_section is None:
        protobuf_doc_section = []
        nav.append({'Protobuf Documentation': protobuf_doc_section})

    node_section = {'Node': node_nav_entries}
    provider_section = {'Provider': provider_nav_entries}
    
    # Clear existing sections and add new ones
    protobuf_doc_section.clear()
    protobuf_doc_section.append(node_section)
    protobuf_doc_section.append(provider_section)

    mkdocs_yml['nav'] = nav

    with open(mkdocs_yml_path, 'w') as f:
        yaml.dump(mkdocs_yml, f, default_flow_style=False)

    print(f"mkdocs.yml updated with new navigation entries.")

def main():
    doc_paths = {
        'node': os.path.join('docs', 'node.md'),
        'provider': os.path.join('docs', 'provider.md')
    }
    mkdocs_yml_path = 'mkdocs.yml'  # Path to the mkdocs.yml file

    for category, doc_path in doc_paths.items():
        preprocess_md_file(doc_path)  # Preprocess the markdown file to clean up headings
    
    node_nav_entries = parse_protobuf_documentation(doc_paths['node'], 'node')
    provider_nav_entries = parse_protobuf_documentation(doc_paths['provider'], 'provider')
    
    update_mkdocs_yml(node_nav_entries, provider_nav_entries, mkdocs_yml_path)

if __name__ == "__main__":
    main()
