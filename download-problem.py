#! /usr/bin/python

import requests
import argparse
import logging
import os
from bs4 import BeautifulSoup as bs

# http://codeforces.com/problemset/problem/96/A

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='Pring debug messages', default=False, action='store_true')
parser.add_argument('url', help='Url of the codeforces problem')

args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

res = requests.get(url=args.url)
soup = bs(res.text, 'html')

problemStatement = soup.find('div', attrs={'class' : 'problem-statement'})
number = [x.strip() for x in soup.find('title').text.split()][2]
name = ''.join(soup.find('div', attrs={'class':'title'}).text.split()[1:])
dirname = '{}-{}'.format(number, name)

print(number, name, dirname)

if not os.path.isdir(dirname):
    os.mkdir(dirname)

template = open('./Main.template', 'r').read(-1)
if not os.path.exists(os.path.join(dirname, 'Main.java')):
    with open(os.path.join(dirname, 'Main.java'), 'w') as f:
        f.write(template % (dirname))

samples = soup.find('div', attrs={'class':'sample-tests'})
inputs = samples.findAll('div', attrs={'class':'input'})
outputs = samples.findAll('div', attrs={'class':'output'})

for i, inputDiv in enumerate(inputs):
    filename = os.path.join(dirname, 'input-{}.in'.format(i))
    with open(filename, 'w') as f:
        f.write('\n'.join([str(x) for x in inputDiv.find('pre').contents if str(x)[0] != '<']))
        f.write('\n')

for i, outputDiv in enumerate(outputs):
    filename = os.path.join(dirname, 'output-{}.out'.format(i))
    with open(filename, 'w') as f:
        f.write('\n'.join([str(x) for x in outputDiv.find('pre').contents if str(x)[0] != '<']))
        f.write('\n')

shfile = os.path.join(dirname, 'execute.sh')
with open(shfile, 'w') as f:
    f.write('#! /bin/bash +x\n\n')
    f.write('javac Main.java\n')
    for i in range(len(inputs)):
        f.write('echo Executing input-{}.in\n'.format(i))
        f.write('java Main < input-{}.in | diff - output-{}.out\n'.format(i, i))
