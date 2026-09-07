import sys
with open(r'D:\Vijyant\arohalims\git\uat_new\arohalims\apps\invoices\utility.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'def upload_to_s3' in line:
        print(f"Line {i+1}: {line.strip()}")
