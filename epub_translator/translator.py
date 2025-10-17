"""Translation backend based on HuggingFace models."""
from __future__ import annotations

import logging
from typing import Iterable, List

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

LOGGER = logging.getLogger(__name__)


class HuggingFaceTranslator:
    """Wrapper around a HuggingFace translation model."""

    def __init__(
        self,
        model_name: str = "Helsinki-NLP/opus-mt-en-id",
        device: str | None = None,
        max_length: int = 512,
    ) -> None:
        self.model_name = model_name
        self.max_length = max_length
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        LOGGER.info("Loading translation model %s on device %s", model_name, self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

    def translate_batch(self, sentences: Iterable[str]) -> List[str]:
        sentences = [sentence for sentence in sentences]
        if not sentences:
            return []

        inputs = self.tokenizer(
            sentences,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.max_length,
        )
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                max_length=self.max_length,
                num_beams=4,
            )

        outputs = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
        return outputs


__all__ = ["HuggingFaceTranslator"]
