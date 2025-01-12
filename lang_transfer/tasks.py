import functools
import itertools
import os

import seqio
import tensorflow as tf

from lang_transfer import preprocessing


DEFAULT_BYTE_OUTPUT_FEATURES = {
    "inputs": seqio.Feature(vocabulary=seqio.ByteVocabulary(), required=False),
    "targets": seqio.Feature(vocabulary=seqio.ByteVocabulary()),
}

DEFAULT_PRE_PROCESSORS = [
    functools.partial(
        seqio.preprocessors.rekey, key_map={"inputs": None, "targets": "text"}
    ),
    seqio.preprocessors.tokenize,
    preprocessing.group_texts,
    seqio.preprocessors.append_eos_after_trim,
]


ALL_LANGUAGES = (
    "ar",
    "en",
    "es",
    "pt",
    "zh",
    "fi",
    "de",
    "ko",
    "id",
    "ja",
    "ru",
)

DATASET_SIZES = [
    "6M",
    "19M",
    "60M",
    "189M",
    "600M",
    "6B",
]

BUCKET_NAME=os.environ.get("BUCKET_NAME", "lang_agnostic_europe")

# ---------------- Language tasks -----------------

# ADD TRAIN datasets for all languages and sizes
print("Using Bucket", BUCKET_NAME, "as source of data.")


for lang, size_name in itertools.product(ALL_LANGUAGES, DATASET_SIZES):
    seqio.TaskRegistry.add(
        f"langagnostic.{lang}.{size_name}",
        source=seqio.TFExampleDataSource(
            {
                "train": f"gs://{BUCKET_NAME}/dataset/{lang}/mc4_{lang}_train_{size_name}.tfrecord",
            },
            feature_description={
                "text": tf.io.FixedLenFeature([], tf.string, default_value=""),
            },
        ),
        preprocessors=DEFAULT_PRE_PROCESSORS,
        output_features=DEFAULT_BYTE_OUTPUT_FEATURES,
        metric_fns=[],
    )

# ADD VALIDATION datasets for all languages
for lang in ALL_LANGUAGES:
    seqio.TaskRegistry.add(
        f"langagnostic.{lang}.validation",
        source=seqio.TFExampleDataSource(
            {
                "validation": f"gs://{BUCKET_NAME}/dataset/{lang}/mc4_{lang}_validation_6B-slice.tfrecord",
            },
            feature_description={
                "text": tf.io.FixedLenFeature([], tf.string, default_value=""),
            },
        ),
        preprocessors=DEFAULT_PRE_PROCESSORS,
        output_features=DEFAULT_BYTE_OUTPUT_FEATURES,
        metric_fns=[],
    )
