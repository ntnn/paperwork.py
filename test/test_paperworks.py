#License: MIT
#Author: Nelo Wallus, http://github.com/ntnn
import unittest
from unittest.mock import call, patch
from paperworks import paperwork, wrapper, models
from json import dumps, loads
import tempfile

notebook_id = '1'
notebook2_id = '2'
new_notebook_id = '2'
notebook_title = 'notebook title'
notebook = {
   'id': notebook_id,
   'title': notebook_title
   }
notebook2 = {
   'id': notebook2_id,
   'title': notebook_title
   }
notebooks = [
   notebook,
   notebook2
   ]

version_id = '10'
version2_id = '11'
version = {
        'id': version_id
        }
version2 = {
        'id': version2_id
        }
versions = [
        version,
        version2
        ]

attachment_id = '55'
attachment2_id = '56'
attachment_file = 'attached.pdf'
attachment = {
        'id': attachment_id,
        'file': attachment_file
        }
attachment2 = {
        'id': attachment2_id,
        'file': attachment_file
        }
attachments = [
        attachment,
        attachment2
        ]

tag_id = '42'
tag2_id = '43'
tag_title = 'some_tag'

tag = {
       'id': tag_id,
       'title': tag_title,
       'visibility': 0
       }
tag2 = {
        'id': tag2_id,
        'title': tag_title,
        'visibility': 0
        }
tags = [
        tag,
        tag2
        ]

note_title = 'note title'
content = 'some content'
note_id = '4'
note2_id = '5'

note = {
   'id': note_id,
   'title': note_title,
   'content': content,
   'notebook_id': notebook_id,
   'tags': [
       tag
       ],
   'versions': [
           version
           ]
        }
note2 = {
        'id': note2_id,
        'title': note_title,
        'content': content,
        'notebook_id': notebook_id,
        'tags': [
            tag2
            ],
        'versions': [
            version2
            ]
        }
notes = [
        note,
        note2
        ]

keyword = 'test keyword'
keyword_b64 = 'dGVzdCBrZXl3b3Jk'

user = 'testuser'
passwd = 'testpassword'
upasswd = 'dGVzdHVzZXI6dGVzdHBhc3N3b3Jk'
uri = 'test/uri'
uri_correct = 'http://test/uri'
agent = 'dummy agent'

move = [{
        'notebook': notebook,
        'id': note_id,
        'notebook_id': notebook_id,
        'version_id': version_id
        }]

tagged = [
        note
        ]

search = [
        note2
        ]

i18n = {
        'holy': 'moly',
        'giant': 'dict'
        }

i18nkey = {
        'giant': 'dict' #not so much
        }

ret = {
        'notebooks':   notebooks,
        'notebook':    notebook,
        'notes':       notes,
        'note':        note,
        'move':        move,
        'versions':    versions,
        'version':     version,
        'attachments': attachments,
        'attachment':  attachment,
        'tags':        tags,
        'tag':         tag,
        'tagged':      tagged,
        'search':      search,
        'i18n':        i18n,
        'i18nkey':     i18n
        }

class TestRequests(unittest.TestCase):
    def setUp(self):
        self.api = wrapper.api(user, passwd, uri, agent)
        self.patcher = patch('paperworks.wrapper.urlopen')
        self.mocked_urlopen = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_b64(self):
        self.assertEqual(wrapper.b64(keyword), keyword_b64)

    def test_init(self):
        self.assertEqual(self.api.host, uri_correct)
        self.assertEqual(self.api.headers['User-Agent'], agent)
        self.assertEqual(self.api.headers['Authorization'], 'Basic ' + upasswd)

    def request(self, function, keyword, *args):
        temp = tempfile.TemporaryFile()
        temp.write(dumps(
                {
                'success': True,
                'response': ret[keyword]
                }
            ).encode('ASCII'))
        temp.seek(0)
        self.mocked_urlopen.return_value = temp

        response = function(*args)

        temp.close()

        self.mocked_urlopen.assert_called()
        self.assertEqual(response, ret[keyword])

    def test_list_notebooks(self):
        self.request(self.api.list_notebooks, 'notebooks')

    def test_create_notebook(self):
        self.request(self.api.create_notebook, 'notebooks', notebook_title)

    def test_get_notebook(self):
        self.request(self.api.get_notebook, 'notebook', notebook_id)

    def test_update_notebook(self):
        self.request(self.api.update_notebook, 'notebook', notebook)

    def test_remove_notebook(self):
        self.request(self.api.remove_notebook, 'notebook', notebook_id)

    def test_list_notebook_notes(self):
        self.request(self.api.list_notebook_notes, 'notes', notebook_id)

    def test_create_note(self):
        self.request(self.api.create_note, 'notes', notebook_id, note_title, content)

    def test_get_note(self):
        self.request(self.api.get_note, 'note', notebook_id, note_id)

    def test_get_notes(self):
        self.request(self.api.get_notes, 'note', notebook_id, notes)

    def test_update_note(self):
        self.request(self.api.update_note, 'note', note)

    def test_remove_note(self):
        self.request(self.api.remove_note, 'notes', note)

    def test_remove_notes(self):
        self.request(self.api.remove_notes, 'notes', notes)

    def test_move_note(self):
        self.request(self.api.move_note, 'move', note, new_notebook_id)

    def test_move_notes(self):
        self.request(self.api.move_notes, 'move', notes, new_notebook_id)

    def test_list_note_versions(self):
        self.request(self.api.list_note_versions, 'versions', note)

    def test_list_notes_versions(self):
        self.request(self.api.list_notes_versions, 'versions', notes)

    def test_get_note_version(self):
        self.request(self.api.get_note_version, 'version', note, version_id)

    def test_list_note_attachments(self):
        self.request(self.api.list_note_attachments, 'attachments', note)

    def test_get_note_attachment(self):
        self.request(self.api.get_note_attachment, 'attachment', note, attachment_id)

    def test_remove_note_attachment(self):
        self.request(self.api.remove_note_attachment, 'attachment', note, attachment_id)

    # TODO (Nelo Wallus): Fix actual method
    @unittest.expectedFailure
    def test_upload_attachment(self):
        self.request(self.api.upload_attachment, 'attachments', note, attachment)

    def test_list_tags(self):
        self.request(self.api.list_tags, 'tags')

    def test_get_tag(self):
        self.request(self.api.get_tag, 'tag', tag_id)

    def test_list_tagged(self):
        self.request(self.api.list_tagged, 'tagged', tag_id)

    def test_search(self):
        self.request(self.api.search, 'search', keyword)

    def test_i18n(self):
        self.request(self.api.i18n, 'i18n')

    def test_i18n_param(self):
        self.request(self.api.i18n, 'i18nkey', keyword)

class TestPaperwork(unittest.TestCase):
    def setUp(self):
        self.pw = paperwork.Paperwork(user, passwd)

    def tearDown(self):
        pass

    def test_parse_json_tag(self):
        parsed_tag = self.pw.parse_json_tag(tag)
        self.assertEqual(parsed_tag.id, tag['id'])
        self.assertEqual(parsed_tag.title, tag['title'])
        self.assertEqual(parsed_tag.visibility, tag['visibility'])

    def test_parse_json_note(self):
        parsed_tag = self.pw.parse_json(tag)
        self.pw.add_tag(parsed_tag)
        self.pw.add_notebook(self.pw.parse_json_notebook(notebook))
        parsed_note = self.pw.parse_json_note(note)
        parsed_note.add_tag(parsed_tag)
        self.assertEqual(parsed_note.id, note['id'])
        self.assertEqual(parsed_note.title, note['title'])
        self.assertTrue(self.pw.find_tag(parsed_tag.title) in parsed_note.tags)

    def test_parse_json_notebook(self):
        parsed_notebook = self.pw.parse_json_notebook(notebook)
        self.assertEqual(parsed_notebook.id, notebook['id'])
        self.assertEqual(parsed_notebook.title, notebook['title'])

    @patch('paperworks.wrapper.api.list_tags')
    @patch('paperworks.wrapper.api.list_notebooks')
    @patch('paperworks.wrapper.api.list_notebook_notes')
    def test_download(self, mocked_list_tags, mocked_list_notebooks, mocked_list_notebook_notes):
        mocked_list_tags.return_value( tags )
        mocked_list_notebooks( notebooks )
        mocked_list_notebook_notes( notes )
        self.pw.download()
        mocked_list_tags.assert_called()
        mocked_list_notebooks.assert_called()
        mocked_list_notebook_notes.assert_called()

    @patch('paperworks.wrapper.api.update_notebook')
    @patch('paperworks.wrapper.api.update_note')
    def test_upload(self, mocked_update_notebook, mocked_update_note):
        parsed_notebook = self.pw.parse_json(notebook)
        self.pw.add_notebook(parsed_notebook)
        self.pw.add_tag(self.pw.parse_json(tag))
        parsed_notebook.add_note(self.pw.parse_json(note))
        self.pw.upload()
        mocked_update_notebook.assert_called()
        mocked_update_note.assert_called()

class TestModel(unittest.TestCase):
    def setUp(self):
        self.pw = paperwork.Paperwork(user, passwd)
        pass

    def tearDown(self):
        pass

    def create_test(self, model, title):
        self.assertEqual(model.title, title)
        self.assertEqual(model.id, 0)

    def from_json_test(self, model, title, id):
        self.assertEqual(model.title, title)
        self.assertEqual(model.id, id)

    def to_json_test(self, model, title, id):
        self.assertEqual(model['title'], title)
        self.assertEqual(model['id'], id)

class TestNotebook(TestModel):
    def test_creation(self):
        nb = models.Notebook(notebook_title)
        self.create_test(nb, notebook_title)
        self.assertEqual(nb.notes, set())

    def test_from_json(self):
        parsed_notebook = models.Notebook.from_json(notebook)
        self.from_json_test(parsed_notebook, notebook_title, notebook_id)

    def test_to_json(self):
        self.to_json_test(models.Notebook(notebook_title, notebook_id).to_json(), notebook_title, notebook_id)

class TestNote(TestModel):
    def test_creation(self):
        new_note = models.Note(note_title)
        self.create_test(new_note, note_title)
        self.assertEqual(new_note.content, '')

    def test_from_json(self):
        parsed_note = models.Note.from_json(note)
        self.assertEqual(parsed_note.content, content)
        self.from_json_test(parsed_note, note_title, note_id)

    def test_to_json(self):
        new_note = models.Note(note_title, note_id, content)
        new_note.add_tag(models.Tag.from_json(tag))
        models.Notebook(notebook_title).add_note(new_note)
        json_note = new_note.to_json()
        self.assertEqual(json_note['content'], content)
        self.to_json_test(json_note, note_title, note_id)



class TestTag(TestModel):
    def test_creation(self):
        tag = models.Tag(tag_title)
        self.create_test(tag, tag_title)

    def test_to_json(self):
        self.to_json_test(models.Tag(tag_title, tag_id).to_json(), tag_title, tag_id)