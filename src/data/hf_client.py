from __future__ import annotations

import os
from typing import Iterable, Mapping, Any

from datasets import load_dataset


DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"
DATASET_SPLIT = "train"


def _get_hf_token() -> str | None:
    """
    Read the Hugging Face access token from the environment, if present.

    This keeps Phase 1 generic and lets you configure authentication without
    hardcoding secrets.
    """

    return os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")


def load_raw_restaurants() -> Iterable[Mapping[str, Any]]:
    """
    Load raw restaurant rows from the Hugging Face dataset.

    Returns an iterable of dict-like records as provided by `datasets`.
    """

    token = _get_hf_token()
    ds = load_dataset(DATASET_ID, split=DATASET_SPLIT, token=token)
    # `ds` behaves like a list of dict rows.
    return (row for row in ds)


__all__ = ["load_raw_restaurants", "DATASET_ID", "DATASET_SPLIT"]

