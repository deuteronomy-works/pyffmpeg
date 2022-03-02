import sys
import os
from time import sleep


_, token = sys.argv

cwd = os.path.realpath('.')

# Login to GH
with open('token.txt', 'w') as tok:
    tok.write(token)
    print('Finished writing token file')

cmd = 'gh auth login --with-token < token.txt'
os.system(cmd)
print('Authenticated')


BRANCHES = ('build-darwin', 'build-linux', 'build-windows')

for branch in BRANCHES:
    title = "new commits from master"
    body = "new commits from master"
    cmd1 = f'gh pr create --base {branch} --title "{title}" --body "{body}"'
    os.system(cmd1)
    cmd2 = f'gh pr merge {branch} --merge --auto --body "Merged"'
    os.system(cmd2)


print('All Done')
