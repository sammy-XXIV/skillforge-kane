"""Machine-readable CLI used by the generating agent and generated skills."""
import argparse
import os
from pathlib import Path
import platform
import shutil
import sys

from .core import Store, ForgeError, canonical, read_json
from .kane import chrome_binary, process


def parser():
    p = argparse.ArgumentParser(description='Forge real agent skills; admit them only after Kane verification.')
    commands = p.add_subparsers(dest='command', required=True)
    create = commands.add_parser('create', help='Freeze a JSON task contract before authoring.')
    create.add_argument('contract')
    author = commands.add_parser('author', help='Generate a candidate SKILL.md package from a procedure.')
    author.add_argument('id')
    author.add_argument('--objective', required=True, help='Path to plain-English procedure.')
    for name in ('verify', 'run'):
        sub = commands.add_parser(name, help=('Verify a candidate.' if name == 'verify'
                                             else 'Reuse a verified skill, with fresh verification.'))
        sub.add_argument('id')
        sub.add_argument('--values', help='JSON file with variable values.')
        sub.add_argument('--set', action='append', default=[], metavar='NAME=VALUE')
    find = commands.add_parser('find', help='Search only currently verified skills.')
    find.add_argument('query', nargs='?', default='')
    listing = commands.add_parser('list', help='List verified skills, or inspect all states.')
    listing.add_argument('--all', action='store_true')
    repair = commands.add_parser('repair', help='Print frozen criteria and failure context for the coding agent.')
    repair.add_argument('id')
    commands.add_parser('doctor', help='Inspect local prerequisites without running a paid test.')
    return p


def values_for(args):
    if args.values and args.set:
        raise ForgeError('Use --values or --set, not both.')
    if args.values:
        return read_json(args.values)
    values = {}
    for item in args.set:
        key, separator, value = item.partition('=')
        if not separator or key in values:
            raise ForgeError('Each --set must be a unique NAME=VALUE pair.')
        values[key] = value
    return values


def doctor():
    executable = shutil.which(os.environ.get('KANE_BIN', 'kane-cli'))
    chrome = chrome_binary()
    result = {'python': platform.python_version(), 'platform': sys.platform,
              'kane': executable, 'chrome': chrome,
              'ready_to_attempt': bool(executable and chrome),
              'authentication': 'Run kane-cli whoami; ready_to_attempt does not imply signed in.',
              'registry': str(Path(os.environ.get('SKILLFORGE_HOME', '.skillforge')).resolve())}
    if executable:
        version = process([executable, '--version'], 15)
        result['kane_version'] = version['stdout'].strip()
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == 'doctor':
            result = doctor()
            code = 0 if result['ready_to_attempt'] else 2
        else:
            store = Store(os.environ.get('SKILLFORGE_HOME', '.skillforge'))
            if args.command == 'create':
                result = store.create(read_json(args.contract))
            elif args.command == 'author':
                result = store.author(args.id, Path(args.objective).read_text(encoding='utf-8'))
            elif args.command in ('verify', 'run'):
                result = getattr(store, args.command)(args.id, values_for(args))
            elif args.command == 'find':
                result = store.find(args.query)
            elif args.command == 'list':
                result = store.find(include_all=args.all)
            elif args.command == 'repair':
                result = store.repair(args.id)
            code = 1 if isinstance(result, dict) and result.get('passed') is False else 0
        print(canonical(result), end='')
        return code
    except (ForgeError, OSError, ValueError) as exc:
        print(canonical({'ok': False, 'error': str(exc)}), end='')
        return 2
    except KeyboardInterrupt:
        print(canonical({'ok': False, 'error': 'Interrupted. Any in-progress skill remains unverified.'}), end='')
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
