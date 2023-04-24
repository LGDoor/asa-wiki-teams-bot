#!/usr/bin/env python3
import sys
from bot.gpt import ask, load_index, build_index


def command_ask():
    
    # Uncomment the below lines to check the underlying API calls 
    # import logging
    # logging.root.setLevel(level=logging.DEBUG)

    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} ask "How are you?"')
        sys.exit(-1)

    load_index()
    query = sys.argv[2]
    answer = ask(query)
    print('Q: ' + query)
    print('A: ' + str(answer))


def command_build():
    if len(sys.argv) != 4:
        print(f'Usage: {sys.argv[0]} build <input_dir> <output_index_file>')
        sys.exit(-1)

    build_index(sys.argv[2], sys.argv[3])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <ask|build> ...')
        sys.exit(-1)

    command = sys.argv[1]
    if command == 'ask':
        command_ask()
    elif command == 'build':
        command_build()
    else:
        print(f'Usage: {sys.argv[0]} <ask|build> ...')
        sys.exit(-1)
