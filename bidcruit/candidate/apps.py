from django.apps import AppConfig


class CandidateConfig(AppConfig):
    name = 'candidate'
    def ready(self):
        print("We are all set!!!!")
        import candidate.signals
        print("signals imported")
