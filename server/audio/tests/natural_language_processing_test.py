import unittest

from server.audio import natural_language_processing


class SpeechToTextTest(unittest.TestCase):

    def test_action_1(self):
        expected_actions = 'apruebe la auditoría'
        text = 'Avisarle a Gaston que apruebe la auditoría'
        result = natural_language_processing.analyze_action(text)
        self.assertEqual(result, expected_actions, f"Should be {expected_actions}")

    def test_action_2(self):
        expected_actions = 'habilitar la sucursal'
        text = 'Guardia propia hay que llamar a Juan y habilitar la sucursal'
        result = natural_language_processing.analyze_action(text)
        self.assertEqual(result, expected_actions, f"Should be {expected_actions}")

    def test_entity_1(self):
        expected_entity = ['Gaston']
        text = 'Avisarle a Gaston que apruebe la auditoría'
        result = natural_language_processing.analyze_entities(text)
        self.assertEqual(result, expected_entity, f"Should be {expected_entity}")

    def test_entity_2(self):
        expected_entity = ['Gaston', 'Maria']
        text = 'Avisarle a Gaston y Maria que aprueben la auditoría'
        result = natural_language_processing.analyze_entities(text)
        self.assertEqual(result, expected_entity, f"Should be {expected_entity}")

    def test_split_basic_flow(self):
        expected_response = 'no tiene'
        expected_note = ' pero habria que arreglarlo'
        text = "No tiene pero habria que arreglarlo"
        result = natural_language_processing.split(text)
        self.assertEqual(result['response'], expected_response, f"Should be {expected_response}")
        self.assertEqual(result['note'], expected_note, f"Should be {expected_note}")

    def test_split_incident_flow_1(self):
        """
        Specific thing from the language must not affect the test: 'ó' should be the same as 'o'.
        """
        expected_response = 'remesa sin habilitacion'
        expected_note = ' hay que avisarle a jose que habilite la remesa'
        expected_incident = {'user': 'Jose', 'action': 'habilite la remesa'}
        text = "Remesa sin habilitación hay que avisarle a Jose que habilite la remesa"
        result = natural_language_processing.split(text)
        print(expected_response)
        print(expected_note)
        print(expected_incident)
        print(result)

        self.assertEqual(result['response'], expected_response, f"Should be {expected_response}")
        self.assertEqual(result['note'], expected_note, f"Should be {expected_note}")
        self.assertEqual(result['incident'], expected_incident, f"Should be {expected_incident}")

    def test_split_incident_flow_2(self):
        expected_response = 'guardia propia'
        expected_note = ' hay que llamar a juan y habilitar la sucursal'
        expected_incident = {'user': 'Juan', 'action': 'habilitar la sucursal'}
        text = "Guardia propia hay que llamar a Juan y habilitar la sucursal"
        result = natural_language_processing.split(text)
        self.assertEqual(result['response'], expected_response, f"Should be {expected_response}")
        self.assertEqual(result['note'], expected_note, f"Should be {expected_note}")
        self.assertEqual(result['incident'], expected_incident, f"Should be {expected_incident}")


if __name__ == '__main__':
    unittest.main()
