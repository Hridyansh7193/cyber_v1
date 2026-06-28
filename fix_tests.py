import os
import glob
import re

wrapper_names = ['Subfinder', 'Assetfinder', 'Gau', 'Trufflehog', 'LinkFinder', 'SecretFinder']

for filepath in glob.glob('tests/unit/execution/**/*.py', recursive=True):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Revert GraphQL to Graphql (the file uses GraphQLPlugin)
    content = content.replace('GraphqlPlugin', 'GraphQLPlugin')
    
    # Revert Wrapper -> Plugin replacements for the specific ones
    for name in wrapper_names:
        content = re.sub(fr'{name}Plugin', f'{name}Wrapper', content)
        content = re.sub(fr'import {name}Wrapper', f'import {name}Wrapper', content)
        content = re.sub(fr'{name}Wrapper\(\)', f'{name}Wrapper()', content)
        
    with open(filepath, 'w') as f:
        f.write(content)
