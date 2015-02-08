#!/usr/bin/env python3

from paperworks import models
import os
import sys
import logging
import yaml
import argparse
import tempfile

if str(sys.version[0]) < '3':
    input = raw_input

logger = logging.getLogger(__name__)

pw = None

att_note_sep = ' to '
note_nb_sep = ' in '


def login():
    """Creates Paperwork instance.
    Reads credentials from rc-file or prompts."""
    global pw
    rc = os.environ.get('HOME')+'/.paperworkrc'
    if os.path.exists(rc):
        with open(rc, 'r') as f:
            conf = yaml.load(f)
        host = conf['host']
        user = conf['user']
        passwd = conf['pass']
    else:
        from getpass import getpass
        host = input('Host:')
        user = input('User:')
        passwd = getpass('Password:')
    pw = models.Paperwork(user, passwd, host)
    if not pw.authenticated:
        print('User/password not valid or host not reachable.')
        sys.exit()


def download():
    """Fills Paperwork instance with information from server."""
    pw.download()


def update():
    """Synchronizes local and remote information."""
    pw.update()


def print_all():
    """Prints notebook and notes in alphabetical order."""
    for nb in pw.get_notebooks():
        print(nb.title)
        for note in nb.get_notes():
            print("- {}".format(note.title))
            for attachment in note.attachments:
                print("-- {}".format(attachment.title))


def split(args, splitter):
    """Splits string with splitter and returns the resulting strings,

    if the splitter is in the string. If not None and the string is returned.
    :type args: str
    :type splitter: str
    :rtype: list
    """
    if splitter in args:
        return args.split(splitter)
    else:
        return None, args


def split_args(args):
    """Splits sring into attachment, note and notebook string.

    :type args: str
    :rtype: list
    """
    attachment, args = split(args, att_note_sep)
    note, notebook = split(args, note_nb_sep)
    return attachment, note, notebook


def split_and_search_args(args):
    """Parses attachment, note and notebook.

    Returns a list of three items with [attachment, note, notebook]
    :type args: str
    :param bool search: If true the method searches for objects and
        returns them instead of strings.
    :rtype: list
    """
    attachment, note, notebook = split_args(args)
    notebook = pw.fuzzy_find(notebook, pw.notebooks)
    if note:
        note = pw.fuzzy_find(note, notebook.notes)
    if attachment:
        attachment = pw.fuzzy_find(attachment, note.attachments)
    return attachment, note, notebook


def prompt(text, important=False):
    """Prompts user for confirmation.

    :type text: str
    :param bool important: If true the default answer is false.
    :rtype: bool
    """
    answers = ('y', 'Y', 'yes', 'Yes', 'YES')
    text += ' y/N' if important else ' Y/n'
    if not important:
        answers += ('',)
    answer = input(text + ' ')
    if answer in answers:
        return True
    return False


def edit(title):
    """Edit note with title.

    :type title: str
    """
    note = split_and_search_args(title)[1]
    logger.info('Getting $EDITOR')
    editor = os.environ.get('EDITOR')

    tmpfile = tempfile.NamedTemporaryFile()

    logger.info('Writing content to temporary file')
    with open(tmpfile, 'w') as f:
        f.write(note.content)

    logger.info('Launching system editor')
    os.system("{} '{}'".format(editor, tmpfile.name))

    logger.info('Reading contents of temporary file')
    with open(tmpfile, 'r') as f:
        note.content = f.read()

    logger.info('Removing temporary file')
    tmpfile.close()

    logger.info('Updating remote note')
    note.update()


def delete(args):
    """Delete note, notebook or attachment, depending on input.

    :type args: str
    """
    attachment, note, notebook = split_and_search_args(args)
    if attachment:
        if prompt('Delete attachment {} to {} in {}?'.format(
                attachment.title, note.title, notebook.title)):
            attachment.delete()
    elif note:
        if prompt('Delete note {} in {}?'.format(
                note.title, notebook.title)):
            note.delete()
    else:
        if prompt('Delete notebook {}?'.format(notebook.title)):
            pw.delete_notebook(notebook)


def move(args):
    """Move a note to another notebook.

    :type args: str
    """
    # splits off the new notebook at the end first, so it
    # doesn't mess with the split_args function
    args, notebook = split(args, ' to ')
    notebook = pw.fuzzy_find(notebook, pw.notebooks)
    note = split_and_search_args(args)[1]
    if prompt('Move note {} to {}?'.format(note.title, notebook.title)):
        note.move_to(notebook)


def create(args):
    """Creates note or notebook, depending on input.

    :type args: str
    """
    if note_nb_sep in args:
        note, notebook = split_args(args)[1:]
        notebook = pw.fuzzy_find(notebook, pw.notebooks)
        if prompt('Create note {} in {}?'.format(note, notebook.title)):
            notebook.create_note(note)
    else:
        if prompt('Create notebook {}?'.format(args)):
            pw.create_notebook(args)


def tags():
    """Lists tags."""
    for tag in pw.get_tags():
        print(tag.title)


def tag(args):
    """Create a tag or tag a note with a tag, depending on input.

    :type args: str
    """
    if ' with ' in args:
        # Again, split tag before
        args, tag = split(args, ' with ')
        tag = pw.fuzzy_find(tag, pw.tags)
        note = split_and_search_args(args)[1]
        if prompt('Tag note {} with {}?'.format(note.title, tag.title)):
            note.add_tag(tag)
    else:
        if prompt('Create tag {}?'.format(args)):
            pw.add_tag(args)


def tagged(tag_title):
    """Print notes tagged with tag.

    :type tag_title: str
    """
    tag = pw.fuzzy_find(tag_title, pw.tags)
    print('Notes tagged with {}'.format(tag.title))
    for note in tag.notes:
        print(note.title)


def upload(args):
    filepath, note, notebook = split_args(args)
    notebook = pw.fuzzy_find(notebook, pw.notebooks)
    note = pw.fuzzy_find(note, notebook.notes)
    note.upload_file(filepath)


def print_help():
    print("""The commands are self-explanatory. Notes, tags and notebooks are chosen through a fuzzy search.

update                                      Pushes local changes to the remote host
ls                                          List notebooks and notes
edit $note                                  edit note
delete $notebook                            delete notebook
delete $note in $notebook                   delete note in notebook
delete $attachment to $note in $notebook    Delete attachment to note in notebook
upload $filepath to $note in $notebook      Upload file at $filepath as attachment to note in notebook
move $note to $notebook                     move note to notebook
create $note in $notebook                   create note in notebook
create $notebook                            create notebook
tags                                        list tags
tag $note with $tag                         tag note with tag
tag $tag                                    create $tag
tagged $tag                                 print notes tagged with $tag
exit                                        exit application
"""
          )

cmd_dict = {
    'update': update,
    'ls': print_all,
    'edit': edit,
    'delete': delete,
    'move': move,
    'create': create,
    'tags': tags,
    'tag': tag,
    'tagged': tagged,
    'help': print_help,
    'upload': upload
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", help="verbose output", action="store_true")
    parser.add_argument(
        "--threading", help="enable multi-threading", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    if args.threading:
        models.use_threading = True
    login()
    download()

    cmd = input('>')
    while (cmd != 'exit'):
        logger.info(cmd)
        if ' ' in cmd:
            cmd = cmd.split(' ', 1)
            args = cmd[1]
            cmd = cmd[0]
        else:
            args = None
        if cmd in cmd_dict.keys():
            if args:
                cmd_dict[cmd](args)
            else:
                cmd_dict[cmd]()
        else:
            logger.info('Invalid command')
            print('{} unknown'.format(cmd))
        cmd = input('>')

if __name__ == "__main__":
    main()
