#!python
# -*- coding: utf-8 -*-
"""Unit testing for scriptorium"""

import os
import tempfile
import shutil
import textwrap
import unittest

import scriptorium

class TestScriptorium(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
      """Set up unit tests for scriptorium"""
      TestScriptorium.template_dir = tempfile.mkdtemp()
      TestScriptorium.paper_dir = tempfile.mkdtemp()
      scriptorium.CONFIG['TEMPLATE_DIR'] = TestScriptorium.template_dir
      scriptorium.install_template("https://github.com/jasedit/ieee.git")
      scriptorium.install_template("https://github.com/jasedit/simple_templates.git")

    @classmethod
    def tearDownClass(cls):
      """Tear down unit test structure."""
      shutil.rmtree(TestScriptorium.template_dir, ignore_errors=True)
      shutil.rmtree(TestScriptorium.paper_dir, ignore_errors=True)

    def testTemplates(self):
      """Test that template has been installed"""
      self.assertEqual(TestScriptorium.template_dir, scriptorium.CONFIG['TEMPLATE_DIR'])
      self.assertTrue(os.path.exists(os.path.join(TestScriptorium.template_dir, 'simple_templates')))
      ex_tdir = os.path.join(scriptorium.CONFIG['TEMPLATE_DIR'], 'simple_templates', 'ieeetran')
      self.assertEqual(scriptorium.find_template('ieeetran'), ex_tdir)

    def testCreation(self):
      """Test simple paper creation."""
      example_config = {
      'author': 'John Doe',
      'title': 'Example Report'
      }

      old_dir = os.getcwd()
      os.chdir(TestScriptorium.paper_dir)
      self.assertEqual(scriptorium.create('ex_report', 'report', config=example_config), set())
      os.chdir('ex_report')
      self.assertEqual(scriptorium.paper_root('.'), 'paper.mmd')
      self.assertEqual(scriptorium.get_template('paper.mmd'), 'report')

      example_text = textwrap.dedent("""\n
        # Introduction

        This is an example paper.

        # Conclusion

        This paper is awesome.
        """)

      with open('paper.mmd', 'a') as fp:
        fp.write(example_text)

      pdf_path = scriptorium.to_pdf('.')

      self.assertTrue(os.path.exists(pdf_path))

      os.chdir(old_dir)

    def testConfigLoading(self):
      """Test saving and loading configuration."""
      config = scriptorium.CONFIG.copy()
      scriptorium.save_config()
      scriptorium.read_config()
      self.assertEqual(config, scriptorium.CONFIG)

    def testConfiguration(self):
      """Test configuration option issues"""
      test_template_dir = "~/.scriptorium"
      scriptorium.CONFIG['TEMPLATE_DIR'] = test_template_dir
      scriptorium.save_config()
      scriptorium.read_config()

      self.assertEqual(scriptorium.CONFIG['TEMPLATE_DIR'], os.path.expanduser(test_template_dir))
      scriptorium.CONFIG['TEMPLATE_DIR'] = self.template_dir

if __name__ == '__main__':
    unittest.main()
