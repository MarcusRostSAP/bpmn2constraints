
from tqdm import tqdm

from bpmnsignal.parser.bpmn_parser import Parser
from bpmnsignal.utils.script_utils import Setup
from bpmnsignal.utils.plot import Plot

FAIL = "failed"
SUCCESS = "successful"

class ParserScript():
    def __init__(self, path) -> None:
        self.path = path
        self.setup = Setup(path)
        self.plot = Plot()
        self.failed_models = 0
        self.successful_models = 0
        self.total_models = 0
        self.total_elements = 0
        self.total_parsed_elements = 0
        self.parsed_models = []

    def _create_scatter_object(self, model_outcome, element_count, type_count):
        return {
            "outcome": model_outcome,
            "number of elements": element_count,
            "number of element types": type_count
        }


    def _create_partial_object(self, percentage, element_count, type_count):
        return {
            "variable": percentage,
            "number of elements": element_count,
            "number of element types": type_count
        }

    def run(self):
        for filename in tqdm(self.setup.get_files()):
            csv_file = self.setup.get_file(filename)

            if self.setup.is_file(csv_file):
                for chunk in self.setup.read_csv_chunk(csv_file):
                    models = self.setup.load_models(chunk)

                    for model in models:
                        try:
                            parser = Parser(model, False, False)

                            if parser.count_pools() > 1:
                                continue

                            result = parser.run()

                            if not parser.has_start():
                                continue

                            if parser.count_model_elements() < 5:
                                continue

                            model_elements = parser.count_model_elements()
                            model_element_types = parser.count_model_element_types()

                            self.total_models += 1
                            parsed = len(result)
                            parsable = parser.count_parsable_elements()

                            self.total_parsed_elements += parsed
                            self.total_elements += parsable

                            if parsed == parsable:
                                # Success
                                self.successful_models += 1
                                self.parsed_models.append(self._create_scatter_object(
                                    SUCCESS, model_elements, model_element_types))

                        except Exception:
                            # Failed
                            self.failed_models += 1
                            # For some reason, I have to subtract here..
                            self.successful_models -= 1
                            self.parsed_models.append(self._create_scatter_object(
                                FAIL, model_elements, model_element_types))

        self.plot.scatter_plot_model_outcomes(self.parsed_models, "All Parsed Models")
        self.plot.bar_plot_model_outcomes(self.parsed_models)

        print(f"Successful: {self.successful_models} out of {self.total_models}")
        print(f"Failed: {self.failed_models} out of {self.total_models}")
        print(f"Parsed {self.total_parsed_elements} out of {self.total_elements} elements.")