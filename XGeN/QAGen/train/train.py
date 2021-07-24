import argparse
import os
import random

import json
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import pytorch_lightning as pl


from transformers import (
    AdamW,
    T5ForConditionalGeneration,
    T5Tokenizer,
    get_linear_schedule_with_warmup
)

def set_seed(seed):
  random.seed(seed)
  np.random.seed(seed)
  torch.manual_seed(seed)
  if torch.cuda.is_available():
    torch.cuda.manual_seed_all(seed)

def get_dataset(tokenizer, type_path, args):
  return BooleanDataset(tokenizer=tokenizer, data_dir=args.data_dir, type_path=type_path,  max_len=args.max_seq_length)


class T5FineTuner(pl.LightningModule):
    def __init__(self, hparams):
        super(T5FineTuner, self).__init__()
        self.hparams = hparams

        self.model = T5ForConditionalGeneration.from_pretrained(hparams.model_name_or_path)
        self.tokenizer = T5Tokenizer.from_pretrained(hparams.tokenizer_name_or_path)

    def is_logger(self):
        return True

    def forward(
            self, input_ids, attention_mask=None, decoder_input_ids=None, decoder_attention_mask=None, labels=None
    ):
        return self.model(
            input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            labels=labels,
        )

    def _step(self, batch):
        labels = batch["target_ids"]
        labels[labels[:, :] == self.tokenizer.pad_token_id] = -100

        outputs = self(
            input_ids=batch["source_ids"],
            attention_mask=batch["source_mask"],
            labels=labels,
            decoder_attention_mask=batch['target_mask']
        )

        loss = outputs[0]

        return loss

    def training_step(self, batch, batch_idx):
        loss = self._step(batch)

        return {"loss": loss}

    def validation_step(self, batch, batch_idx):
        loss = self._step(batch)
        return {"val_loss": loss}

    def configure_optimizers(self):
        "Prepare optimizer and schedule (linear warmup and decay)"

        model = self.model
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": self.hparams.weight_decay,
            },
            {
                "params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
        ]
        optimizer = AdamW(optimizer_grouped_parameters, lr=self.hparams.learning_rate, eps=self.hparams.adam_epsilon)
        self.opt = optimizer
        return [optimizer]

    def optimizer_step(self, epoch, batch_idx, optimizer, optimizer_idx, second_order_closure=None):
        optimizer.step()
        optimizer.zero_grad()
        self.lr_scheduler.step()

    def train_dataloader(self):
        train_dataset = get_dataset(tokenizer=self.tokenizer, type_path="boolq_train", args=self.hparams)
        dataloader = DataLoader(train_dataset, batch_size=self.hparams.train_batch_size, drop_last=True, shuffle=True,
                                num_workers=4)
        t_total = (
                (len(dataloader.dataset) // (self.hparams.train_batch_size * max(1, self.hparams.n_gpu)))
                // self.hparams.gradient_accumulation_steps
                * float(self.hparams.num_train_epochs)
        )
        scheduler = get_linear_schedule_with_warmup(
            self.opt, num_warmup_steps=self.hparams.warmup_steps, num_training_steps=t_total
        )
        self.lr_scheduler = scheduler
        return dataloader

    def val_dataloader(self):
        val_dataset = get_dataset(tokenizer=self.tokenizer, type_path="boolq_val", args=self.hparams)
        return DataLoader(val_dataset, batch_size=self.hparams.eval_batch_size, num_workers=4)





class BooleanDataset(Dataset):
    # def __init__(self, tokenizer, data_dir, type_path, max_len=256):
    #     self.path = os.path.join(data_dir, type_path + '.csv')

    #     self.passage_column = "passage"
    #     self.true_false = "answer"
    #     self.target_column = "question"
    #     self.title = "title"
    #     self.data = pd.read_csv(self.path)

    #     self.max_len = max_len
    #     self.tokenizer = tokenizer
    #     self.inputs = []
    #     self.targets = []

    #     self._build()

    def __init__(self, tokenizer, data_dir, type_path, max_len=256):
        self.path = os.path.join(data_dir, type_path + '.json')

        self.passage_column = "passage"
        self.true_false = "answer"
        self.target_column = "question"
        self.title = "title"
        self.data = None

        with open(self.path, 'r') as f:
            self.data = json.load(f)
        
        self.max_len = max_len
        self.tokenizer = tokenizer
        self.inputs = []
        self.targets = []

        self._build()

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, index):
        source_ids = self.inputs[index]["input_ids"].squeeze()
        target_ids = self.targets[index]["input_ids"].squeeze()

        src_mask = self.inputs[index]["attention_mask"].squeeze()  # might need to squeeze
        target_mask = self.targets[index]["attention_mask"].squeeze()  # might need to squeeze

        return {"source_ids": source_ids, "source_mask": src_mask, "target_ids": target_ids, "target_mask": target_mask}

    def _build(self):
        for idx in range(len(self.data)):
            passage = self.data[self.passage_column]
            true_false = self.data[self.true_false]
            target = self.data[self.target_column]
                        # passage,true_false,target = self.data.loc[idx, self.passage_column],self.data.loc[idx, self.true_false], self.data.loc[idx, self.target_column]
            true_false = str(true_false)
            if true_false.lower() =="true":
                true_false ="yes"
            else:
                true_false = "no"
            # input_ = "paraphrase: "+ input_ + ' </s>'
            input_ = "truefalse: %s passage: %s </s>" % (true_false,passage)
            target = target + " </s>"

            # tokenize inputs
            tokenized_inputs = self.tokenizer.batch_encode_plus(
                [input_], max_length=self.max_len, pad_to_max_length=True, return_tensors="pt"
            )
            # tokenize targets
            tokenized_targets = self.tokenizer.batch_encode_plus(
                [target], max_length=self.max_len, pad_to_max_length=True, return_tensors="pt"
            )

            self.inputs.append(tokenized_inputs)
            self.targets.append(tokenized_targets)



set_seed(42)

args_dict = dict(
    data_dir="XGeN/google_boolq_data", # path for data files
    output_dir="XGeN_Model", # path to save the checkpoints
    model_name_or_path='valhalla/t5-base-qa-qg-hl',
    tokenizer_name_or_path='t5-base',
    max_seq_length=256,
    learning_rate=3e-4,
    weight_decay=0.0,
    adam_epsilon=1e-8,
    warmup_steps=0,
    train_batch_size=6,
    eval_batch_size=6,
    num_train_epochs=4,
    gradient_accumulation_steps=16,
    n_gpu=1,
    early_stop_callback=False,
    fp_16=False, # if you want to enable 16-bit training then install apex and set this to true
    opt_level='O1', # you can find out more on optimisation levels here https://nvidia.github.io/apex/amp.html#opt-levels-and-properties
    max_grad_norm=1.0, # if you enable 16-bit training then set this to a sensible value, 0.5 is a good default
    seed=42,
)

train_path = "XGeN/google_boolq_data/boolq_train.csv"
val_path = "XGeN/google_boolq_data/boolq_val.csv"

train = pd.read_csv(train_path)

tokenizer = T5Tokenizer.from_pretrained('t5-base')

dataset = BooleanDataset(tokenizer, 'XGeN/google_boolq_data', 'boolq_val', 256)
print("Val dataset: ",len(dataset))

data = dataset[2]
print(tokenizer.decode(data['source_ids']))
print(tokenizer.decode(data['target_ids']))

if not os.path.exists('XGeN_Model'):
    os.makedirs('XGeN_Model')

args = argparse.Namespace(**args_dict)
print(args_dict)

checkpoint_callback = pl.callbacks.ModelCheckpoint(
    filepath=args.output_dir, prefix="checkpoint", monitor="val_loss", mode="min", save_top_k=1
)

train_params = dict(
    accumulate_grad_batches=args.gradient_accumulation_steps,
    gpus=args.n_gpu,
    max_epochs=args.num_train_epochs,
    early_stop_callback=False,
    precision= 16 if args.fp_16 else 32,
    amp_level=args.opt_level,
    gradient_clip_val=args.max_grad_norm,
    checkpoint_callback=checkpoint_callback,
)


print ("Initialize model")
model = T5FineTuner(args)

trainer = pl.Trainer(**train_params)

print (" Training model")
trainer.fit(model)

print ("training finished")

print ("Saving model")
model.model.save_pretrained('XGeN_Model')

print ("Saved model")