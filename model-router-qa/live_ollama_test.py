"""Live Ollama smoke test; runs only on isolated CI runner with tiny model."""
import os, tempfile, unittest
from pathlib import Path
from router import Ollama, RouterError, execute
class LiveOllama(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.model=os.environ.get("DEVNET_TEST_MODEL","smollm2:135m")
  cls.client=Ollama(timeout=240)
  models=cls.client.call("/api/tags").get("models",[])
  if cls.model not in {m["name"] for m in models}: raise RuntimeError("Required test model not pulled")
 def test_01_load_and_unload(self):
  c=self.client
  self.assertFalse(c.loaded()-{self.model},"foreign model present")
  c.load(self.model);self.assertIn(self.model,c.loaded())
  c.unload(self.model);self.assertNotIn(self.model,c.loaded())
 def test_02_response_and_retention(self):
  c=self.client
  answer=c.run(self.model,"Reply with just the word OK.",retain=True)
  self.assertTrue(answer.strip())
  self.assertIn(self.model,c.loaded(),"default model should remain resident")
  c.unload(self.model)
 def test_03_no_foreign_model_unloading(self):
  c=self.client
  original=c.loaded
  try:
   c.loaded=lambda: {"foreign:latest"}
   with self.assertRaises(RouterError): c.switch("default:latest",self.model,"test")
  finally: c.loaded=original
if __name__=="__main__": unittest.main()
