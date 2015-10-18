# encoding: utf-8
"""
This script tests ``GitIgnorePattern``.
"""

import unittest

import pathspec.util
from pathspec import GitIgnorePattern

class GitIgnoreTest(unittest.TestCase):
	"""
	The ``GitIgnoreTest`` class tests the ``GitIgnorePattern``
	implementation.
	"""

	def test_00_empty(self):
		"""
		Tests an empty pattern.
		"""
		spec = GitIgnorePattern('')
		self.assertIsNone(spec.include)
		self.assertIsNone(spec.regex)

	def test_01_absolute_root(self):
		"""
		Tests a single root absolute path pattern.

		This should NOT match any file (according to git check-ignore (v2.4.1)).
		"""
		spec = GitIgnorePattern('/')
		self.assertIsNone(spec.include)
		self.assertIsNone(spec.regex)

	def test_01_absolute(self):
		"""
		Tests an absolute path pattern.

		This should match:
		an/absolute/file/path
		an/absolute/file/path/foo

		This should NOT match:
		foo/an/absolute/file/path
		"""
		spec = GitIgnorePattern('/an/absolute/file/path')
		self.assertTrue(spec.include)
		self.assertEqual(spec.regex.pattern, '^an/absolute/file/path(?:/.*)?$')

	def test_01_relative(self):
		"""
		Tests a relative path pattern.

		This should match:
		spam
		spam/
		foo/spam
		spam/foo
		foo/spam/bar
		"""
		spec = GitIgnorePattern('spam')
		self.assertTrue(spec.include)
		self.assertEqual(spec.regex.pattern, '^(?:.+/)?spam(?:/.*)?$')

	def test_01_relative_nested(self):
		"""
		Tests a relative nested path pattern.

		This should match:
		foo/spam
		foo/spam/bar

		This should **not** match (according to git check-ignore (v2.4.1)):
		bar/foo/spam
		"""
		spec = GitIgnorePattern('foo/spam')
		self.assertTrue(spec.include)
		self.assertEqual(spec.regex.pattern, '^foo/spam(?:/.*)?$')

	def test_02_comment(self):
		"""
		Tests a comment pattern.
		"""
		spec = GitIgnorePattern('# Cork soakers.')
		self.assertIsNone(spec.include)
		self.assertIsNone(spec.regex)

	def test_02_ignore(self):
		"""
		Tests an exclude pattern.

		This should NOT match (according to git check-ignore (v2.4.1)):
		temp/foo
		"""
		spec = GitIgnorePattern('!temp')
		self.assertIsNotNone(spec.include)
		self.assertFalse(spec.include)
		self.assertEqual(spec.regex.pattern, '^(?:.+/)?temp$')

	def test_03_child_double_asterisk(self):
		"""
		Tests a directory name with a double-asterisk child
		directory.

		This should match:
		spam/bar

		This should **not** match (according to git check-ignore (v2.4.1)):
		foo/spam/bar
		"""
		spec = GitIgnorePattern('spam/**')
		self.assertTrue(spec.include)
		self.assertEqual(spec.regex.pattern, '^spam/.*$')

	def test_03_inner_double_asterisk(self):
		"""
		Tests a path with an inner double-asterisk directory.

		This should match:
		left/bar/right
		left/foo/bar/right
		left/bar/right/foo

		This should **not** match (according to git check-ignore (v2.4.1)):
		foo/left/bar/right
		"""
		spec = GitIgnorePattern('left/**/right')
		self.assertTrue(spec.include)
		self.assertEqual(spec.regex.pattern, '^left(?:/.+)?/right(?:/.*)?$')

	def test_03_only_double_asterisk(self):
		"""
		Tests a double-asterisk pattern which matches everything.
		"""
		spec = GitIgnorePattern('**')
		self.assertTrue(spec.include)
		self.assertEqual(spec.regex.pattern, '^.+$')

	def test_03_parent_double_asterisk(self):
		"""
		Tests a file name with a double-asterisk parent directory.

		This should match:
		foo/spam
		foo/spam/bar
		"""
		spec = GitIgnorePattern('**/spam')
		self.assertTrue(spec.include)
		self.assertEqual(spec.regex.pattern, '^(?:.+/)?spam(?:/.*)?$')

	def test_04_infix_wildcard(self):
		"""
		Tests a pattern with an infix wildcard.

		This should match:
		foo--bar
		foo-hello-bar
		a/foo-hello-bar
		foo-hello-bar/b
		a/foo-hello-bar/b
		"""
		spec = GitIgnorePattern('foo-*-bar')
		self.assertTrue(spec.include)
		self.assertEqual(spec.regex.pattern, '^(?:.+/)?foo\\-[^/]*\\-bar(?:/.*)?$')

	def test_04_postfix_wildcard(self):
		"""
		Tests a pattern with a postfix wildcard.

		This should match:
		~temp-
		~temp-foo
		~temp-foo/bar
		foo/~temp-bar
		foo/~temp-bar/baz
		"""
		spec = GitIgnorePattern('~temp-*')
		self.assertTrue(spec.include)
		self.assertEqual(spec.regex.pattern, '^(?:.+/)?\\~temp\\-[^/]*(?:/.*)?$')

	def test_04_prefix_wildcard(self):
		"""
		Tests a pattern with a prefix wildcard.

		This should match:
		bar.py
		bar.py/
		foo/bar.py
		foo/bar.py/baz
		"""
		spec = GitIgnorePattern('*.py')
		self.assertTrue(spec.include)
		self.assertEqual(spec.regex.pattern, '^(?:.+/)?[^/]*\\.py(?:/.*)?$')

	def test_05_directory(self):
		"""
		Tests a directory pattern.

		This should match:
		dir/
		foo/dir/
		foo/dir/bar

		This should **not** match:
		dir
		"""
		spec = GitIgnorePattern('dir/')
		self.assertTrue(spec.include)
		self.assertEqual(spec.regex.pattern, '^(?:.+/)?dir/.*$')

	def test_05_registered(self):
		"""
		Tests that the pattern is registered.
		"""
		self.assertIs(pathspec.util.lookup_pattern('gitignore'), GitIgnorePattern)


if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(GitIgnoreTest)
	unittest.TextTestRunner(verbosity=2).run(suite)
