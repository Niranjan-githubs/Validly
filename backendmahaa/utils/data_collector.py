# data_collector.py

class DataCollector:
    def __init__(self, questions):
        self.questions = questions

    def collect_responses(self):
        responses = {}
        for key, question in self.questions.items():
            responses[key] = input(f"{question}\n> ").strip()
        return responses 