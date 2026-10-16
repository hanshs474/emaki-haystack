# emaki-haystack

[Haystack](https://haystack.deepset.ai) components for emaki (emaki.ai), the Japanese-language AI video generator for Seedance 2.5 and Seedance 2.0. Render [Seedance 2.5](https://emaki.ai/seedance-2-5) clips, [image to video](https://emaki.ai/image-to-video) and AI images inside a pipeline on one [emaki](https://emaki.ai/?utm_source=pypi-haystack&utm_medium=package) API key.

```bash
pip install emaki-haystack
export EMAKI_API_KEY=sk-...   # create one at https://emaki.ai/settings/apikeys
```

```python
from emaki_haystack import EmakiImageGenerator, EmakiVideoGenerator

EmakiVideoGenerator(duration=5).run(prompt="a lighthouse beam sweeping across fog at night, slow push-in")
# {"videos": ["https://cdn.emaki.ai/..."]}

EmakiImageGenerator(aspect_ratio="16:9").run(prompt="a lighthouse in fog, long exposure")
# {"images": ["https://cdn.emaki.ai/..."]}
```

## In a pipeline

Write the shot with an LLM, render it with Seedance 2.5:

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from emaki_haystack import EmakiVideoGenerator

p = Pipeline()
p.add_component("brief", PromptBuilder("Write one video prompt for a 5-second product teaser about {{topic}}. Name the action and the camera move."))
p.add_component("llm", OpenAIGenerator())
p.add_component("render", EmakiVideoGenerator(duration=5, aspect_ratio="9:16"))
p.connect("brief", "llm")
p.connect("llm.replies", "render.prompt")
```

(`llm.replies` is a list; add a small adapter component that takes `replies[0]` if your Haystack version does not convert it.)

## Components

| Component | `run()` input | Output |
|---|---|---|
| `EmakiVideoGenerator` | `prompt`, optional `image_url` (first frame) | `{"videos": [url]}` |
| `EmakiImageGenerator` | `prompt` | `{"images": [url]}` |

`EmakiVideoGenerator` takes `model`, `duration`, `resolution`, `aspect_ratio` and `generate_audio` at init. It defaults to `seedance_2_5`; `seedance_2` ([Seedance 2.0](https://emaki.ai/seedance-2)), `seedance_2_fast`, `seedance_2_mini`, `minimax_h3` and `veo_3_1` are the other ids. `EmakiImageGenerator` defaults to `nano_banana_2_lite`. Both serialize with `to_dict` / `from_dict`; the key is a Haystack `Secret` read from `EMAKI_API_KEY`.

Each run costs credits on your emaki account, the same price as on the website. Errors raise the `emaki` client's exceptions (`AuthError`, `QuotaError`, `PlanError`, `BusyError`, `RejectedError`, `GenerationFailed`) so a pipeline can branch on them. Finished clips can be sharpened with the [AI video upscaler](https://emaki.ai/video-upscaler).

日本語での使い方は [シーダンス](https://emaki.ai/) へ。

Built on the [`emaki`](https://pypi.org/project/emaki/) client. MIT licensed. Made by [emaki](https://emaki.ai/?utm_source=pypi-haystack&utm_medium=package).
