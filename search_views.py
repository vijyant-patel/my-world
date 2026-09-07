import sys
with open(r'D:\Vijyant\arohalims\git\uat_new\arohalims\apps\samples\views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'CreateCustomFieldValuesApi' in line or 'UpdateCustomFieldValuesApi' in line:
        print(f"Line {i+1}: {line.strip()}")
