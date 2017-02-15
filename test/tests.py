#!python
# -*- coding: utf-8 -*-
"""Unit testing for scriptorium"""

import os
import tempfile
import shutil
import unittest

import scriptorium

class TestScriptorium(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
      """Set up unit tests for scriptorium"""
      TestScriptorium.template_dir = tempfile.mkdtemp()
      TestScriptorium.paper_dir = tempfile.mkdtemp()
      scriptorium.CONFIG['TEMPLATE_DIR'] = TestScriptorium.template_dir
      scriptorium.install_template("https://github.com/jasedit/simple_templates.git")

    @classmethod
    def tearDownClass(cls):
      """Tear down unit test structure."""
      shutil.rmtree(TestScriptorium.template_dir)
      shutil.rmtree(TestScriptorium.paper_dir)

    def testTemplates(self):
      """Test that template has been installed"""
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
      self.assertTrue(os.path.exists('.'))

      os.chdir(old_dir)

if __name__ == '__main__':
    unittest.main()