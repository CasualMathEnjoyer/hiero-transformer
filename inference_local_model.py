import string

import datasets
import pandas as pd
import torch
from tqdm.auto import tqdm
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

from utils import lang_to_m2m_lang_id, load_data_from_folder
# script to test custom model on custom test data

# Load data
raw_data = load_data_from_folder("test_ramses")

# Simple processing for ramses data (metadata fields are empty)
# Extract ea -> tnt (transliteration) based on presence of source and transliteration fields
test_data = {"ea": {"tnt": []}}
for datapoint in raw_data:
    if "source" in datapoint and "transliteration" in datapoint:
        if datapoint["source"] != "" and datapoint["transliteration"] != "":
            test_data["ea"]["tnt"].append({
                "source": datapoint["source"],
                "target": datapoint["transliteration"]
            })

print(f"Processed {len(test_data['ea']['tnt'])} datapoints for ea -> tnt")


# Load model to generate predictions

# model = M2M100ForConditionalGeneration.from_pretrained("mattiadc/hiero-transformer").to("cuda:0").eval()
# tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

checkpoint_path = "/home/katka/hieroglyphs/checkpoint_total_steps=12000_loss=0.50"
model = M2M100ForConditionalGeneration.from_pretrained(checkpoint_path).to("cuda:0").eval()
tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

# Produce predictions
for src_lang, values in test_data.items():
    for tgt_lang, data in values.items():
        print(f"\n{src_lang} -> {tgt_lang}: {len(data)} samples")
        for element in tqdm(data):
            with torch.no_grad():
                with torch.cuda.amp.autocast():
                    tokenizer.src_lang = lang_to_m2m_lang_id[src_lang]
                    tokenizer.tgt_lang = lang_to_m2m_lang_id[tgt_lang]

                    model_inputs = tokenizer(
                        [element["source"]], return_tensors="pt"
                    ).to(model.device)
                    generated_tokens = model.generate(
                        **model_inputs,
                        num_beams=10,
                        forced_bos_token_id=tokenizer.get_lang_id(
                            lang_to_m2m_lang_id[tgt_lang]
                        )
                    )
                    element["prediction"] = tokenizer.batch_decode(
                        generated_tokens, skip_special_tokens=True
                    )[0]

# Save predictions to file
output_file = "predictions.txt"
print(f"\nSaving predictions to {output_file}...")
with open(output_file, 'w', encoding='utf-8') as f:
    for src_lang, values in test_data.items():
        for tgt_lang, data in values.items():
            for element in data:
                f.write(element["prediction"] + "\n")
print(f"Saved {sum(len(data) for values in test_data.values() for data in values.values())} predictions to {output_file}")

# Calculate metrics
metrics = {
    src_lang: {
        tgt_lang: {m: datasets.load_metric(m) for m in ("sacrebleu", "rouge")}
        for tgt_lang, _ in values.items()
    }
    for src_lang, values in test_data.items()
}
for src_lang, values in test_data.items():
    for tgt_lang, data in values.items():
        if len(data) == 0:
            continue
        for element in data:
            for metric in metrics[src_lang][tgt_lang].values():
                metric.add_batch(
                    predictions=[
                        element["prediction"].strip(string.punctuation).lower().split()
                    ],
                    references=[
                        [element["target"].strip(string.punctuation).lower().split()]
                    ],
                )

computed_metrics = {
    src_lang: {
        tgt_lang: {name: metric.compute() for name, metric in metric_dict.items()}
        for tgt_lang, metric_dict in values.items()
        if len(test_data[src_lang][tgt_lang]) > 0
    }
    for src_lang, values in metrics.items()
    if any(len(test_data[src_lang][tgt_lang]) > 0 for tgt_lang in values.keys())
}

# Compute tables
tables = {
    "sacrebleu": {
        src_lang: {
            tgt_lang: metric["sacrebleu"]["score"]
            for tgt_lang, metric in values.items()
        }
        for src_lang, values in computed_metrics.items()
    },
    "rougeL": {
        src_lang: {
            tgt_lang: 100 * metric["rouge"]["rougeL"].mid.fmeasure
            for tgt_lang, metric in values.items()
        }
        for src_lang, values in computed_metrics.items()
    },
}

print("\n" + "="*50)
print("RESULTS")
print("="*50)
print("\nsacrebleu")
print(pd.DataFrame(tables["sacrebleu"]).T)
print("\nrougeL")
print(pd.DataFrame(tables["rougeL"]).T)
