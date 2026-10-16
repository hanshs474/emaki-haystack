from unittest import mock

import emaki
import pytest
from haystack.utils import Secret
from emaki_haystack import EmakiImageGenerator, EmakiVideoGenerator


def test_image():
    with mock.patch.object(emaki, "generate_image", return_value="https://cdn.emaki.ai/i.png") as g:
        out = EmakiImageGenerator(aspect_ratio="16:9", api_key=Secret.from_token("sk")).run(prompt="a boat")
    assert out == {"images": ["https://cdn.emaki.ai/i.png"]}
    assert g.call_args.args[1] == "nano_banana_2_lite"
    assert g.call_args.kwargs["api_key"] == "sk"
    assert g.call_args.kwargs["aspect_ratio"] == "16:9"


def test_video_and_roundtrip(monkeypatch):
    monkeypatch.setenv("EMAKI_API_KEY", "sk-env")
    gen = EmakiVideoGenerator(duration=6, resolution="720p")
    gen2 = EmakiVideoGenerator.from_dict(gen.to_dict())
    with mock.patch.object(emaki, "generate_video", return_value="https://cdn.emaki.ai/v.mp4") as g:
        assert gen2.run(prompt="a fox", image_url="https://x/y.png") == {"videos": ["https://cdn.emaki.ai/v.mp4"]}
    assert g.call_args.args[1] == "seedance_2_5"
    assert g.call_args.kwargs["api_key"] == "sk-env"
    assert g.call_args.kwargs["image"] == "https://x/y.png"
    assert g.call_args.kwargs["duration"] == 6
    assert "aspect_ratio" not in g.call_args.kwargs


def test_auth_error_propagates():
    def transport(method, url, body, headers):
        return 401, {"error": "Invalid API key. Create one at https://emaki.ai/settings/apikeys"}

    real = emaki.generate_video
    with mock.patch.object(emaki, "generate_video", side_effect=lambda *a, **k: real(*a, transport=transport, **k)):
        with pytest.raises(emaki.AuthError):
            EmakiVideoGenerator(api_key=Secret.from_token("sk-bad")).run(prompt="x")
