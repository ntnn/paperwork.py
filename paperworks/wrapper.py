# License: MIT
# Author: Nelo Wallus, http://github.com/ntnn

try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen
from base64 import b64encode
import logging
import json


logger = logging.getLogger('paperwork-wrapper')

__version__ = '0.12'
api_version = '/api/v1/'
user_agent = 'paperwork.py v{}'.format(__version__)

api_path = {
    'notebooks':   'notebooks',
    'notebook':    'notebooks/{}',
    'notes':       'notebooks/{}/notes',
    'note':        'notebooks/{}/notes/{}',
    'move':        'notebooks/{}/notes/{}/move/{}',
    'versions':    'notebooks/{}/notes/{}/versions',
    'version':     'notebooks/{}/notes/{}/versions/{}',
    'attachments': 'notebooks/{}/notes/{}/versions/{}/attachments',
    'attachment':  'notebooks/{}/notes/{}/versions/{}/attachments/{}',
    'tags':        'tags',
    'tag':         'tags/{}',
    'tagged':      'tagged/{}',
    'search':      'search/{}',
    'i18n':        'i18n',
    'i18nkey':     'i18n/{}'
    }


def b64(string):
    """Returns given string as base64 hash."""
    return b64encode(string.encode('UTF-8')).decode('ASCII')


class api:
    def __init__(
            self,
            user,
            passwd,
            uri='http://demo.paperwork.rocks/',
            user_agent=user_agent):
        self.host = uri if 'http://' in uri else 'http://' + uri
        self.headers = {
            'Application-Type': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + b64('{}:{}'.format(user, passwd)),
            'Connection': 'keep-alive',
            'User-Agent': user_agent
            }

    def request(self, data, method, keyword, *args):
        """Sends a request to the host and returns the parsed json data
        if successfull.

        :type method: func
        :type keyword: str
        :rtype: dict or None
        """
        try:
            if data:
                data = json.dumps(data).encode('ASCII')
            uri = self.host + api_version + api_path[keyword].format(*args)
            data, files = None, None
            if 'file' in kwargs:
                self.headers['Content-Type'] = 'multipart/form-data'
                files = kwargs
            elif kwargs:
                self.headers['Content-Type'] = 'application/json'
                data = json.dumps(kwargs)
            logger.info(
                '{} request to {}:\ndata: {}\nfiles: {}\nheaders:{}'.format(
                    method, uri, data, files, self.headers))
            request = method(uri, data=data, files=files, headers=self.headers)
            res = request.text
            logger.info(res)
            if keyword == 'attachment_raw':
                return res
            json_res = json.loads(res)
            if json_res['success'] is False:
                logger.error('Unsuccessful request.')
            else:
                return json_res['response']
        except Exception as e:
            logger.error(e)

    def get(self, keyword, *args):
        """Convenience wrapper for GET request.

        :type keyword: str
        :rtype: dict or list or None
        """
        return self.request(requests.get, keyword, *args)

    def post(self, data, keyword, *args):
        """Convenience wrapper for POST request.

        :type data: dict
        :type keyword: str
        :rtype: dict or list or None
        """
        return self.request(requests.post, keyword, *args, **data)

    def put(self, data, keyword, *args):
        """Convenience wrapper for PUT request.

        :type data: dict
        :type keyword: str
        :rtype: dict or list or None
        """
        return self.request(requests.put, keyword, *args, **data)

    def delete(self, keyword, *args):
        """Convenience wrapper for DELETE request.

        :type keyword: str
        :rtype: dict or list or None
        """
        return self.request(requests.delete, keyword, *args)

    def list_notebooks(self):
        """Return all notebooks in a list."""
        return self.get('notebooks')

    def create_notebook(self, name):
        """Create new notebook with name."""
        return self.post(
            {'type': 0, 'title': name, 'shortcut': ''}, 'notebooks')

    def get_notebook(self, notebook_id):
        """Returns notebook."""
        return self.get('notebook', notebook_id)

    def update_notebook(self, notebook):
        """Updates notebook."""
        return self.put(notebook, 'notebook', notebook['id'])

    def delete_notebook(self, notebook_id):
        """Deletes notebook and all containing notes."""
        return self.delete('notebook', notebook_id)

    def list_notebook_notes(self, notebook_id):
        """Returns notes in notebook in a list."""
        return self.get('notes', notebook_id)

    def create_note(self, notebook_id, note_title, content=''):
        """Creates note with note_title in notebook. Returns note."""
        return self.post(
            {'title': note_title, 'content': content}, 'notes', notebook_id)

    def get_note(self, notebook_id, note_id):
        """Returns note with note_id from notebook with notebook_id."""
        return self.get_notes(notebook_id, [note_id])

    def get_notes(self, notebook_id, note_ids):
        """Returns note with note_id from notebook with notebook_id."""
        return self.get('note', notebook_id, ','.join(
            [str(note_id) for note_id in note_ids]))

    def update_note(self, note):
        """Updates note and returns meta info."""
        return self.put(note, 'note', note['notebook_id'], note['id'])

    def delete_note(self, note):
        """Deletes note and returns meta info."""
        return self.delete_notes([note])

    def delete_notes(self, notes):
        """Deletes note and returns meta info."""
        return self.delete('note', notes[0]['notebook_id'], ','.join(
            [note['id'] for note in notes]))

    def move_note(self, note, new_notebook_id):
        """Moves note to new_notebook_id and returns meta info."""
        return self.move_notes([note], new_notebook_id)

    def move_notes(self, notes, new_notebook_id):
        """Moves notes to new_notebook_id and returns meta info."""
        return self.get('move', notes[0]['notebook_id'], ','.join(
            [note['id'] for note in notes]), new_notebook_id)

    def list_note_versions(self, note):
        """Returns a list of versions of given note."""
        return self.list_notes_versions([note])

    def list_notes_versions(self, notes):
        """Returns lists of versions of given notes."""
        return self.get('versions', notes[0]['notebook_id'], ','.join(
            [note['id'] for note in notes]))

    def get_note_version(self, note, version_id):
        """Returns version with version_id of note."""
        return self.get('version', note['notebook_id'], note['id'], version_id)

    def list_note_attachments(self, note):
        """List attachments to note."""
        return self.get(
            'attachments',
            note['notebook_id'],
            note['id'],
            note['versions'][0]['id'])

    def get_note_attachment(self, note, attachment_id):
        """Returns attachment with attachment_id of note."""
        return self.get(
            'attachment',
            note['notebook_id'],
            note['id'],
            note['versions'][0]['id'],
            attachment_id)

    def delete_note_attachment(self, note, attachment_id):
        """Deletes attachment with attachment_id on note."""
        return self.delete(
            'attachment',
            note['notebook_id'],
            note['id'],
            note['versions'][0]['id'],
            attachment_id)

    # TODO (Nelo Wallus): Create method
    def upload_attachment(self, note, attachment):
        pass

    def list_tags(self):
        """Returns all tags."""
        return self.get('tags')

    def get_tag(self, tag_id):
        """Returns tag with tag_id."""
        return self.get('tag', tag_id)

    def list_tagged(self, tag_id):
        """Returns notes tagged with tag."""
        return self.get('tagged', tag_id)

    def search(self, keyword):
        """Search for notes containing given keyword."""
        return self.get('search', b64(keyword))

    def i18n(self, keyword=None):
        """Returns either the full i18n dict or the requested word."""
        if keyword:
            return self.get('i18nkey', keyword)
        return self.get('i18n')
