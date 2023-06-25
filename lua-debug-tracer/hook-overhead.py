#!/usr/bin/env python

import sys

#hook_functions = {'hookf', 'luaD_hook', 'luaH_getn'}
hook_functions = {'hookf', 'luaD_hook'}

saw_hook_function = False

hook_function_sample_count = 0
non_hook_function_sample_count = 0

for line in sys.stdin:
    if line.startswith('Attaching'):
        continue

    if line.strip() == '':
        continue

    if line.startswith('@[]:'):
        count = int(line.removeprefix('@[]: '))
        non_hook_function_sample_count += count
    elif line.startswith('@['):
        saw_hook_function = False
    elif line.startswith(']:'):
        count = int(line.removeprefix(']: '))
        if saw_hook_function:
            hook_function_sample_count += count
        else:
            non_hook_function_sample_count += count
    elif line.startswith(' '):
        if line.startswith('    hookf') or line.startswith('    luaD_hook'):
            saw_hook_function = True

print(f'Hook function sample count:     {hook_function_sample_count}')
print(f'Non-hook function sample count: {non_hook_function_sample_count}')
