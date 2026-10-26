import unittest
from chatbot import reply, MAX_MESSAGE

class ChatbotTests(unittest.TestCase):
    def test_emergency_priority(self):
        for message in [
            "I have a cold and chest pain", "I CAN’T BREATHE", "chest-pressure",
            "My friend has slurred speech", "one-sided weakness",
            "I took an overdose", "I want to kill myself", "my throat is swelling",
            "I had chest pain yesterday but it stopped", "no chest pain", "What is a stroke?",
        ]:
            with self.subTest(message=message):
                response = reply(message)
                self.assertEqual(response["kind"], "emergency")
                self.assertIn("local emergency number", response["answer"])
                self.assertIn("If this is happening", response["answer"])

    def test_medication_and_diagnosis(self):
        for message in ["ibuprofen dose for fever", "What antibiotic for a cold?",
                        "Can I take warfarin with aspirin?", "Diagnose my fever",
                        "Do I have a cold?", "Interpret blood test results"]:
            with self.subTest(message=message):
                self.assertEqual(reply(message)["kind"], "clinician")

    def test_special_populations(self):
        for message in ["my baby has a fever", "pregnant with a cold", "child hydration",
                        "fever during chemotherapy", "breastfeeding with a cold"]:
            with self.subTest(message=message):
                self.assertEqual(reply(message)["kind"], "clinician")

    def test_sources(self):
        for message, fragment in [("cold", "common-cold"), ("fever", "fever-in-adults"),
                                  ("dehydration", "dehydration")]:
            response = reply(message)
            self.assertEqual(response["kind"], "information")
            self.assertIn(fragment, response["sources"][0]["url"])
            self.assertIn("Cannot diagnose", response["notice"])

    def test_unknown_and_word_boundaries(self):
        for message in ["quantum medicine", "scold", "gold", "rash", "<script>alert(1)</script>"]:
            self.assertEqual(reply(message)["kind"], "clinician")

    def test_greeting_and_appointment(self):
        self.assertIn("Hello", reply("HELLO!")["answer"])
        self.assertIn("allergies", reply("prepare for appointment")["answer"])

    def test_invalid_input(self):
        for message in [None, 1, {}, [], "", "  ", "x" * (MAX_MESSAGE + 1)]:
            with self.subTest(message=repr(message)[:40]):
                with self.assertRaises(ValueError):
                    reply(message)

    def test_length_boundary(self):
        self.assertEqual(reply("x" * MAX_MESSAGE)["kind"], "clinician")

if __name__ == "__main__":
    unittest.main()
