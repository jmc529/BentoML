import pandas
import pytest
import torch
from torch import nn

import bentoml
from bentoml.yatai.client import YataiClient
from tests import PytorchClassifier


class PytorchModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.linear = nn.Linear(5, 1, bias=False)
        torch.nn.init.ones_(self.linear.weight)

    def forward(self, x):
        x = self.linear(x)

        return x


@pytest.fixture()
def pytorch_classifier_class():
    # When the ExampleBentoService got saved and loaded again in the test, the two class
    # attribute below got set to the loaded BentoService class. Resetting it here so it
    # does not effect other tests
    PytorchClassifier._bento_service_bundle_path = None
    PytorchClassifier._bento_service_bundle_version = None
    return PytorchClassifier


test_df = pandas.DataFrame([[1, 1, 1, 1, 1]])


def test_pytorch_artifact_pack(pytorch_classifier_class):
    svc = pytorch_classifier_class()
    model = PytorchModel()
    svc.pack("model", model)
    assert svc.predict(test_df) == 5.0, "Run inference before save the artifact"

    saved_path = svc.save()
    loaded_svc = bentoml.load(saved_path)
    assert loaded_svc.predict(test_df) == 5.0, "Run inference from saved artifact"

    # clean up saved bundle
    yc = YataiClient()
    yc.repository.delete(f"{svc.name}:{svc.version}")


def test_pytorch_artifact_pack_with_traced_model(pytorch_classifier_class):
    svc = pytorch_classifier_class()
    input_for_tracing = torch.ones(5)
    model = PytorchModel()
    traced_model = torch.jit.trace(model, input_for_tracing)

    svc.pack("model", traced_model)
    assert svc.predict(test_df) == 5.0, "Run inference before save the artifact"

    saved_path = svc.save()
    loaded_svc = bentoml.load(saved_path)
    assert loaded_svc.predict(test_df) == 5.0, "Run inference from saved artifact"

    # clean up saved bundle
    yc = YataiClient()
    yc.repository.delete(f"{svc.name}:{svc.version}")


def test_pytorch_artifact_pack_with_scripted_model(pytorch_classifier_class):
    svc = pytorch_classifier_class()
    model = PytorchModel()
    scripted_model = torch.jit.script(model)

    svc.pack("model", scripted_model)
    assert svc.predict(test_df) == 5.0, "Run inference before save the artifact"

    saved_path = svc.save()
    loaded_svc = bentoml.load(saved_path)
    assert loaded_svc.predict(test_df) == 5.0, "Run inference from saved artifact"

    # clean up saved bundle
    yc = YataiClient()
    yc.repository.delete(f"{svc.name}:{svc.version}")
