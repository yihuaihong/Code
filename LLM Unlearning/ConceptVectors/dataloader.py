import torch
from torch import nn
from transformers import Trainer
from transformers.trainer_utils import seed_worker
from transformers.utils import is_datasets_available
import datasets
from torch.utils.data import DataLoader, Dataset, RandomSampler, SequentialSampler
import torch.nn.functional as F
import copy, os
import copy
import json 
from pathlib import Path
from data_module import get_batch_loss 
from utils import merge_dicts, interleave_eval_result_dict, get_forget_quality, get_model_utility
import numpy as np
from scipy.stats import ks_2samp, hmean
import csv 
import pickle
import math
import re

def printll(name, inp):
    #print list with 4 decimal for each item
    print(name, [round(x, 4) for x in inp])


class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        input_ids, labels, attention_mask = inputs
        outputs = model(input_ids,labels=labels, attention_mask=attention_mask)
        loss = outputs.loss
        return (loss, outputs) if return_outputs else loss
    
    def prediction_step(self, model, inputs, prediction_loss_only: bool, ignore_keys=None):
        input_ids, labels, attention_mask = inputs
        # forward pass
        with torch.no_grad():
            outputs = model(input_ids,labels=labels, attention_mask=attention_mask)
            logits = outputs.logits
            loss = outputs.loss
        return (loss, logits, labels)
    

class CustomTrainerForgetting(Trainer):
    def __init__(self, *args, **kwargs):
        self.loss_type = kwargs.pop('forget_loss')
        self.oracle_model = kwargs.pop('oracle_model')
        self.seed = kwargs.pop('seed')

        # the coefficient of each part in the loss function. This is used in ablation study.
        self.npo_coeff=kwargs.pop('npo_coeff')
        self.grad_diff_coeff=kwargs.pop('grad_diff_coeff')
        self.KL_coeff=kwargs.pop('KL_coeff')

        self.ref_policy = kwargs.pop('ref_policy')

        self.beta = kwargs.pop('beta')

        super(CustomTrainerForgetting, self).__init__(*args, **kwargs)

        # Here, we always need the oracle model to compute the KL distance in the evaluation time.
        # self.oracle_model = self.e_prepare_deepspeed(self.oracle_model) 暂时不用，后面要恢复

    def get_train_dataloader(self):
        """
        Override the original get_train_dataloader function simply for debugging.
        This is identical to the get_train_dataloader function in transformer.Trainer.
        """
        if self.train_dataset is None:
            raise ValueError("Trainer: training requires a train_dataset.")

        train_dataset = self.train_dataset
        data_collator = self.data_collator
        if is_datasets_available() and isinstance(train_dataset, datasets.Dataset):
            train_dataset = self._remove_unused_columns(train_dataset, description="training")
        else:
            data_collator = self._get_collator_with_removed_columns(data_collator, description="training")

        dataloader_params = {
            "batch_size": self._train_batch_size,
            "collate_fn": data_collator,
            "num_workers": self.args.dataloader_num_workers,
            "pin_memory": self.args.dataloader_pin_memory,
            "persistent_workers": self.args.dataloader_persistent_workers,
        }
        
        generator = torch.Generator()
        generator.manual_seed(self.seed + self.state.global_step) #不理解为什么要以这种方式设置seed，直接固定seed不好吗？
        print(f'Generator........Epoch-{self.state.global_step}')

        if not isinstance(train_dataset, torch.utils.data.IterableDataset):
            
            dataloader_params["generator"] = generator
            dataloader_params["shuffle"] = True # set shuffle=True with specified generator.
            # dataloader_params["sampler"] = self._get_train_sampler()
            dataloader_params["drop_last"] = self.args.dataloader_drop_last
            dataloader_params["worker_init_fn"] = seed_worker

        return self.accelerator.prepare(DataLoader(train_dataset, **dataloader_params))


    def e_prepare_deepspeed(self, model):
        # Adapted from accelerate: https://github.com/huggingface/accelerate/blob/739b135f8367becb67ffaada12fe76e3aa60fefd/src/accelerate/accelerator.py#L1473
        deepspeed_plugin = self.accelerator.state.deepspeed_plugin
        config_kwargs = copy.deepcopy(deepspeed_plugin.deepspeed_config)

        if model is not None:
            if hasattr(model, "config"):
                hidden_size = (
                    max(model.config.hidden_sizes)
                    if getattr(model.config, "hidden_sizes", None)
                    else getattr(model.config, "hidden_size", None)
                )
                if hidden_size is not None and config_kwargs["zero_optimization"]["stage"] == 3:
                    # Note that `stage3_prefetch_bucket_size` can produce DeepSpeed messages like: `Invalidate trace cache @ step 0: expected module 1, but got module 0`
                    # This is expected and is not an error, see: https://github.com/microsoft/DeepSpeed/discussions/4081
                    config_kwargs.update(
                        {
                            "zero_optimization.reduce_bucket_size": hidden_size * hidden_size,
                            "zero_optimization.stage3_param_persistence_threshold": 10 * hidden_size,
                            "zero_optimization.stage3_prefetch_bucket_size": 0.9 * hidden_size * hidden_size,
                        }
                    )


        if config_kwargs["zero_optimization"]["stage"] != 3:
            config_kwargs["zero_optimization"]["stage"] = 0
        config_kwargs["optimizer"] = {"type": None}
        model, *_ = deepspeed.initialize(model=model, config=config_kwargs)
        model.eval()
        #set the gradients to false for every parameter
        for param in model.parameters():
            param.requires_grad = False
        
        return model
    

    def compute_loss(self, model, inputs, return_outputs=False):
        if self.loss_type == "grad_ascent":
            forget_inputs = inputs[0]
            input_ids, labels, attention_mask = forget_inputs
            outputs = model(input_ids,labels=labels, attention_mask=attention_mask)
            forget_loss = outputs.loss
            forget_loss = forget_loss * -1
            loss = forget_loss

        elif self.loss_type == "grad_diff":
            forget_inputs, retain_inputs = inputs
            input_ids, labels, attention_mask = forget_inputs
            outputs = model(input_ids,labels=labels, attention_mask=attention_mask)
            forget_loss = outputs.loss
            forget_loss = forget_loss * -1

            retain_input_ids, retain_labels, retain_attention_mask = retain_inputs
            retain_outputs = model(retain_input_ids,labels=retain_labels, attention_mask=retain_attention_mask)
            retain_loss = retain_outputs.loss
            loss = forget_loss + 1.5*retain_loss - (forget_loss + 1.5*retain_loss)
        
        elif self.loss_type in ["dpo","dpo_grad_diff","dpo_KL"]:
            forget_inputs, retain_inputs = inputs
            retain_input_ids, retain_labels, retain_attention_mask = retain_inputs
            forget_input_ids, forget_labels, forget_attention_mask = forget_inputs
            retain_outputs = model(retain_input_ids, labels=retain_labels, attention_mask=retain_attention_mask)
            forget_outputs = model(forget_input_ids, labels=forget_labels, attention_mask=forget_attention_mask)
            with torch.no_grad():
                retain_outputs_oracle = self.oracle_model(retain_input_ids, labels=retain_labels, attention_mask=retain_attention_mask)
                forget_outputs_oracle = self.oracle_model(forget_input_ids, labels=forget_labels, attention_mask=forget_attention_mask)
                retain_logits_oracle = retain_outputs_oracle.logits
                forget_logits_oracle = forget_outputs_oracle.logits

                retain_loss_oracle = -1 * get_batch_loss(retain_logits_oracle, retain_labels)
                forget_loss_oracle = -1 * get_batch_loss(forget_logits_oracle, forget_labels)

            retain_loss_current = -1 * get_batch_loss(retain_outputs.logits, retain_labels)
            forget_loss_current = -1 * get_batch_loss(forget_outputs.logits, forget_labels)

            pi_logratios = retain_loss_current - forget_loss_current
            ref_logratios = retain_loss_oracle - forget_loss_oracle
            loss = -F.logsigmoid(self.beta * (pi_logratios - ref_logratios)).mean() * 2 / self.beta

            if self.loss_type == 'dpo_grad_diff':
                retain_input_ids, retain_labels, retain_attention_mask = retain_inputs
                retain_outputs = model(retain_input_ids,labels=retain_labels, attention_mask=retain_attention_mask)
                retain_loss = retain_outputs.loss
                loss = loss + retain_loss

            elif self.loss_type == 'dpo_KL':
                retain_input_ids, retain_labels, retain_attention_mask = retain_inputs
                with torch.no_grad():
                    retain_outputs = self.oracle_model(retain_input_ids, labels=retain_labels, attention_mask=retain_attention_mask)
                retain_probs = F.log_softmax(retain_outputs.logits, dim=-1)
                retain_probs = retain_probs.view(-1, retain_outputs.logits.shape[-1])

                current_outputs = model(retain_input_ids,labels=retain_labels, attention_mask=retain_attention_mask)
                current_probs = F.log_softmax(current_outputs.logits, dim=-1)
                current_probs = current_probs.view(-1, current_outputs.logits.shape[-1])

                #minimum KL divergence
                retain_loss = nn.functional.kl_div(current_probs, retain_probs, reduction='batchmean', log_target=True)
                loss = loss + retain_loss

        ### Implement the NPO
        elif self.loss_type == 'npo':
            forget_inputs, _ = inputs
            input_ids, labels, attention_mask = forget_inputs
            outputs = model(input_ids,labels=labels, attention_mask=attention_mask)

            forget_loss_current = get_batch_loss(outputs.logits, labels) 

            if self.ref_policy == 'fine_tuned':
                with torch.no_grad():
                    forget_outputs_oracle = self.oracle_model(input_ids, labels=labels, attention_mask=attention_mask)
                    forget_logits_oracle = forget_outputs_oracle.logits
                    forget_loss_oracle = get_batch_loss(forget_logits_oracle, labels)
                neg_log_ratios = forget_loss_current - forget_loss_oracle
            else:
                raise NotImplementedError
            loss = -F.logsigmoid(self.beta * neg_log_ratios).mean() * 2 / self.beta 

        elif self.loss_type == 'npo_grad_diff':
            forget_inputs, retain_inputs = inputs
            input_ids, labels, attention_mask = forget_inputs
            outputs = model(input_ids,labels=labels, attention_mask=attention_mask)
            forget_loss_current = get_batch_loss(outputs.logits, labels) 

            if self.ref_policy == 'fine_tuned':
                with torch.no_grad():
                    forget_outputs_oracle = self.oracle_model(input_ids, labels=labels, attention_mask=attention_mask)
                    forget_logits_oracle = forget_outputs_oracle.logits
                    forget_loss_oracle = get_batch_loss(forget_logits_oracle, labels)
                neg_log_ratios = forget_loss_current - forget_loss_oracle
            else:
                raise NotImplementedError
            forget_loss = -F.logsigmoid(self.beta * neg_log_ratios).mean() * 2 / self.beta

            retain_input_ids, retain_labels, retain_attention_mask = retain_inputs
            retain_outputs = model(retain_input_ids,labels=retain_labels, attention_mask=retain_attention_mask)
            retain_loss = retain_outputs.loss
            loss = self.npo_coeff * forget_loss + self.grad_diff_coeff * retain_loss
            
        elif self.loss_type == 'npo_KL':
            forget_inputs, retain_inputs = inputs
            input_ids, labels, attention_mask = forget_inputs
            outputs = model(input_ids,labels=labels, attention_mask=attention_mask)
            forget_loss_current = get_batch_loss(outputs.logits, labels) 
            if self.ref_policy == 'fine_tuned':
                with torch.no_grad():
                    forget_outputs_oracle = self.oracle_model(input_ids, labels=labels, attention_mask=attention_mask)
                    forget_logits_oracle = forget_outputs_oracle.logits
                    forget_loss_oracle = get_batch_loss(forget_logits_oracle, labels)
                neg_log_ratios = forget_loss_current - forget_loss_oracle
            else:
                raise NotImplementedError
            forget_loss = -F.logsigmoid(self.beta * neg_log_ratios).mean() * 2 / self.beta

            retain_input_ids, retain_labels, retain_attention_mask = retain_inputs
            with torch.no_grad():
                retain_outputs = self.oracle_model(retain_input_ids,labels=retain_labels, attention_mask=retain_attention_mask)
            retain_probs = F.log_softmax(retain_outputs.logits, dim=-1)
            retain_probs = retain_probs.view(-1, retain_outputs.logits.shape[-1])

            current_outputs = model(retain_input_ids,labels=retain_labels, attention_mask=retain_attention_mask)
            current_probs = F.log_softmax(current_outputs.logits, dim=-1)
            current_probs = current_probs.view(-1, current_outputs.logits.shape[-1])

            #minimum KL divergence
            retain_loss = nn.functional.kl_div(current_probs, retain_probs, reduction='batchmean', log_target=True)
            loss = self.npo_coeff * forget_loss + self.KL_coeff * retain_loss


        return (loss, outputs) if return_outputs else loss
        
    
    def prediction_step(self, model, inputs, prediction_loss_only: bool, ignore_keys=None):
        input_ids, labels, attention_mask = inputs
        # forward pass
        with torch.no_grad():
            outputs = model(input_ids,labels=labels, attention_mask=attention_mask)
            logits = outputs.logits
            loss = outputs.loss
        return (loss, logits, labels)


def custom_data_collator_forget(samples):
    rets = []
    if len(samples[0]) == 2:
        forget_samples, retain_samples = [sample[0] for sample in samples], [sample[1] for sample in samples]
        data_types = ["forget", "retain"]
    elif len(samples[0]) == 1:
        forget_samples = [sample[0] for sample in samples]
        data_types = ["forget"]
    for data_type in data_types:
        if data_type == "forget":
            data = forget_samples 
        elif data_type == "retain":
            data = retain_samples
         
        input_ids = [s[0] for s in data]
        labels = [s[1] for s in data]
        attention_mask = [s[2] for s in data]
        rets.append((torch.stack(input_ids), torch.stack(labels), torch.stack(attention_mask)))
    return rets



def get_loss(output, labels):
    shifted_labels = labels[..., 1:].contiguous()
    output = output[..., :-1, :].contiguous()

    loss_function = nn.CrossEntropyLoss(ignore_index=-100)
    loss = loss_function(output.view(-1, output.size(-1)), shifted_labels.view(-1))

    return loss


