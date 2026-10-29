import json, tempfile, unittest
from pathlib import Path
from unittest.mock import Mock
from router import Ollama, RouterError, execute
class Tests(unittest.TestCase):
 def test_reject_remote(self):
  with self.assertRaises(RouterError): Ollama("http://example.com")
 def test_switch_order(self):
  c=Ollama();c.loaded=Mock(side_effect=[{"default"},{"default"},set(),set(),set(),{"default"}])
  c.unload=Mock();c.run=Mock(return_value="answer");c.load=Mock()
  self.assertEqual(c.switch("default","specialist","task"),"answer")
  c.unload.assert_called_once_with("default")
  c.run.assert_called_once_with("specialist","task")
  c.load.assert_called_once_with("default")
 def test_other_model_blocked(self):
  c=Ollama();c.loaded=Mock(return_value={"foreign"})
  with self.assertRaises(RouterError): c.switch("default","specialist","task")
 def test_restore_after_failure(self):
  c=Ollama();c.loaded=Mock(return_value=set());c.run=Mock(side_effect=RouterError("failed"));c.load=Mock()
  with self.assertRaises(RouterError): c.switch("default","specialist","task")
  c.load.assert_called_once_with("default")
 def test_success_checkpoint(self):
  c=Mock();c.switch.return_value="code";c.run.return_value="summary"
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"state.json";self.assertEqual(execute(c,"task","specialist","default",p)["status"],"FINISHED")
   self.assertEqual(json.loads(p.read_text())["status"],"FINISHED")
 def test_failure_checkpoint(self):
  c=Mock();c.switch.side_effect=RouterError("failed")
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"state.json"
   with self.assertRaises(RouterError): execute(c,"task","specialist","default",p)
   self.assertEqual(json.loads(p.read_text())["status"],"BLOCKED")
 def test_no_overwrite(self):
  c=Mock()
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"state.json";p.write_text("original")
   with self.assertRaises(RouterError): execute(c,"task","specialist","default",p)
   self.assertEqual(p.read_text(),"original")
 def test_reject_same_models(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(RouterError): execute(Mock(),"task","same","same",Path(d)/"state.json")
if __name__=="__main__": unittest.main()
