import os

folder = r'e:\Sydney\Z- SCI\Z Group Harjinder\deliverease\frontend\lib'
for root, dirs, files in os.walk(folder):
    for f in files:
        if f.endswith('.dart'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            if '₹' in content:
                content = content.replace('₹', r'\$')
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)
print("Done fixing currency!")
