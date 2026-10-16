"""emaki video and image generation as Haystack components.

emaki (https://emaki.ai) is the Japanese-language AI video generator for
Seedance 2.5 and Seedance 2.0. Both components run on an emaki account: pass
``api_key`` (a Haystack ``Secret``) or set ``EMAKI_API_KEY``. Create a key at
https://emaki.ai/settings/apikeys. Runs cost credits on that account, the same
price as on the website.
"""

from typing import Any, Dict, List, Optional

import emaki
from haystack import component, default_from_dict, default_to_dict
from haystack.utils import Secret, deserialize_secrets_inplace


def _params(**kw: Any) -> Dict[str, Any]:
    return {k: v for k, v in kw.items() if v is not None}


@component
class EmakiVideoGenerator:
    """Generates a clip from a prompt, or animates a still, and returns its URL.

    ``model`` defaults to ``seedance_2_5``; other ids: ``seedance_2``,
    ``seedance_2_fast``, ``seedance_2_mini``, ``minimax_h3``, ``veo_3_1``.

    Usage:
        ```python
        from emaki_haystack import EmakiVideoGenerator

        gen = EmakiVideoGenerator(duration=5, aspect_ratio="9:16")
        gen.run(prompt="a paper boat drifting down a rain gutter, low angle")["videos"]
        ```
    """

    def __init__(
        self,
        model: str = emaki.DEFAULT_VIDEO_MODEL,
        duration: Optional[int] = None,
        resolution: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        generate_audio: Optional[bool] = None,
        api_key: Secret = Secret.from_env_var("EMAKI_API_KEY"),
        timeout: float = 900.0,
    ):
        self.model = model
        self.duration = duration
        self.resolution = resolution
        self.aspect_ratio = aspect_ratio
        self.generate_audio = generate_audio
        self.api_key = api_key
        self.timeout = timeout

    def to_dict(self) -> Dict[str, Any]:
        return default_to_dict(
            self, model=self.model, duration=self.duration, resolution=self.resolution,
            aspect_ratio=self.aspect_ratio, generate_audio=self.generate_audio,
            api_key=self.api_key.to_dict(), timeout=self.timeout,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmakiVideoGenerator":
        deserialize_secrets_inplace(data["init_parameters"], keys=["api_key"])
        return default_from_dict(cls, data)

    @component.output_types(videos=List[str])
    def run(self, prompt: str, image_url: Optional[str] = None) -> Dict[str, List[str]]:
        """Generate one clip, or animate the image at ``image_url`` as the first frame.

        Raises an ``emaki.EmakiError`` subclass on a refusal, an empty balance,
        a failed run or a timeout.
        """
        url = emaki.generate_video(
            prompt,
            self.model,
            api_key=self.api_key.resolve_value(),
            timeout=self.timeout,
            **_params(
                image=image_url,
                duration=self.duration,
                resolution=self.resolution,
                aspect_ratio=self.aspect_ratio,
                generate_audio=self.generate_audio,
            ),
        )
        return {"videos": [url]}


@component
class EmakiImageGenerator:
    """Generates an image from a prompt and returns its URL.

    ``model`` defaults to ``nano_banana_2_lite``, the cheapest; other ids:
    ``nano_banana_2``, ``seedream_5_lite``, ``gpt_image_2``.
    """

    def __init__(
        self,
        model: str = emaki.DEFAULT_IMAGE_MODEL,
        aspect_ratio: Optional[str] = None,
        api_key: Secret = Secret.from_env_var("EMAKI_API_KEY"),
        timeout: float = 900.0,
    ):
        self.model = model
        self.aspect_ratio = aspect_ratio
        self.api_key = api_key
        self.timeout = timeout

    def to_dict(self) -> Dict[str, Any]:
        return default_to_dict(
            self, model=self.model, aspect_ratio=self.aspect_ratio,
            api_key=self.api_key.to_dict(), timeout=self.timeout,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EmakiImageGenerator":
        deserialize_secrets_inplace(data["init_parameters"], keys=["api_key"])
        return default_from_dict(cls, data)

    @component.output_types(images=List[str])
    def run(self, prompt: str) -> Dict[str, List[str]]:
        """Generate one image."""
        url = emaki.generate_image(
            prompt,
            self.model,
            api_key=self.api_key.resolve_value(),
            timeout=self.timeout,
            **_params(aspect_ratio=self.aspect_ratio),
        )
        return {"images": [url]}
