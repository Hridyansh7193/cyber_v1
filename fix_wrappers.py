import glob
import re

for filepath in glob.glob('tests/unit/execution/**/*.py', recursive=True):
    with open(filepath, 'r') as f:
        content = f.read()
    
    # from execution.api.swagger_wrapper import SwaggerWrapper -> import SwaggerPlugin
    content = re.sub(r'import (\w+)Wrapper', r'import \1Plugin', content)
    
    # plugin = SwaggerWrapper() -> plugin = SwaggerPlugin()
    content = re.sub(r'(\w+)Wrapper\(\)', r'\1Plugin()', content)
    
    with open(filepath, 'w') as f:
        f.write(content)
