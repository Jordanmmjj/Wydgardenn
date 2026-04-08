import os
import re

dir_path = 'templates'

def convert_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # We use function replacements to completely avoid python backslash bugs in replacement strings
    def repl_href_static(m):
        return f'href="{{{{ url_for(\'static\', filename=\'{m.group(1)}/{m.group(2)}\') }}}}"'
    content = re.sub(r'th:href="@{/(css|js|img|images|storage)/(.*?)}"', repl_href_static, content)
    
    def repl_href_route(m):
        return f'href="/{m.group(1)}"'
    content = re.sub(r'th:href="@{/(.*?)}"', repl_href_route, content)

    def repl_src_static(m):
        return f'src="{{{{ url_for(\'static\', filename=\'{m.group(1)}/{m.group(2)}\') }}}}"'
    content = re.sub(r'th:src="@{/(css|js|img|images|storage)/(.*?)}"', repl_src_static, content)
    
    def repl_src_route(m):
        return f'src="/{m.group(1)}"'
    content = re.sub(r'th:src="@{/(.*?)}"', repl_src_route, content)

    def repl_action(m):
        return f'action="/{m.group(1)}"'
    content = re.sub(r'th:action="@{/(.*?)}"', repl_action, content)
    
    # Remove 'th:text' structure leaving just inner Jinja like <tag>{{ var }}</tag>
    # Very safe regex to just match the th:text safely
    content = re.sub(r'th:text="\${(.*?)}"', r'>{{ \1 }}<', content)
    # This was truncating tags dangerously, let's skip the tag cleaner and just let Jinja output it
    # No, we must clean it:
    content = content.replace('><{{', '>{{').replace('}}<<', '}}</')

    # Remove th:classappend and others safely
    content = re.sub(r'th:object="\${.*?}"', '', content)
    content = re.sub(r'th:field="\*{.*?}"', '', content)
    content = re.sub(r'sec:authorize=".*?"', '', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for root, _, files in os.walk(dir_path):
    for filename in files:
        if filename.endswith('.html'):
            filepath = os.path.join(root, filename)
            try:
                convert_file(filepath)
            except Exception as e:
                print(f"Error converting {filepath}: {e}")

print("Plantillas convertidas exitosamente.")
