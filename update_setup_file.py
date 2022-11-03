import re


version = os.environ['GITHUB_REF'].split('/')[-1]
print(f'version: {version}')


def replace_setup_file_version():

    sta = '"Development Status :: 5 - Production/Stable"'
    bta = '"Development Status :: 4 - Beta"'

    ver = version.split('-')[0]
    ver = ver.replace('v', '')

    if 'beta' in version:
        beta = version.split('-')[1]
        beta = beta.split('beta.')[1]
        ver += f'b{beta}'

    with open('setup.py', 'r') as f:
        data = f.read()

    repl = re.compile("version='.*?[0-9]'")
    ver_str = f"version='{ver}'"
    data = repl.sub(ver_str, data)

    if 'beta' in version:
        data = data.replace(sta, bta)
    else:
        data = data.replace(bta, sta)

    with open('setup.py', 'w') as fw:
        fw.write(data)
    
    print('Done changing version type')
    

replace_setup_file_version()
