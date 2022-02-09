import sys
import os
from time import sleep


version = os.environ['GITHUB_REF'].split('/')[-1]
print(f'version: {version}')

_, token = sys.argv

cwd = os.path.realpath('.')

# Login to GH
with open('token.txt', 'w') as tok:
    tok.write(token)
    print('Finished writing token file')

cmd = 'gh auth login --with-token < token.txt'
os.system(cmd)
print('Authenticated')

def main():
    BRANCHES = ('build-darwin', 'build-linux', 'build-windows')

    for branch in BRANCHES:
        tag = version + branch.replace('build', '')
        cmd1 = f'gh release create {tag} --target {branch} -p'
        os.system(cmd1)

    print('sleeping for a minute')
    sleep(600)
    print('Should delete tags')
    for branch in BRANCHES:
        tag = version + branch.replace('build', '')
        cmd1 = f'gh release delete {tag} --yes'
        os.system(cmd1)
    print('done deleting tags')

main()

print('All Done')
