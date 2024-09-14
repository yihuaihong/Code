import numpy as np
import torch

def fine_edit_layer(model, tok, input_tok, lookup_idxs, true_target_ids, request, hparams):

    source_index = lookup_idxs[0]

    hooks = set_act_get_hooks(model, source_index, mlp=True)

    output = model(input_ids=input_tok['input_ids'][0], attention_mask=input_tok['attention_mask'][0])

    # remove hooks
    remove_hooks(hooks)

    list_prob = []

    true_target_id = true_target_ids.tolist()[0]

    print(f"look for layer which encode the target token: {true_target_id}")

    if "gpt" in model.config.model_type:
        for layer_idx in hparams.layers:
            # MLP
            mlp_state = model.activations_[f'm_out_{layer_idx}']
            mlp_proj = model.lm_head(mlp_state).detach().cpu().numpy()
            target_mlp_proj = mlp_proj[true_target_id]
            list_prob.append(target_mlp_proj)


    elif "llama" in model.config.model_type:
        for layer_idx in hparams.layers:

            mlp_state = model.activations_[f'm_out_{layer_idx}']
            mlp_proj = model.lm_head(mlp_state).detach().cpu().numpy()

            target_mlp_proj = mlp_proj[true_target_id]
            list_prob.append(target_mlp_proj)


    layers_to_edit = list_prob.index(max(list_prob)) + hparams.layers[0] #e.g. 16 = 3 + 13
    print('layers_to_edit: ',layers_to_edit)

    return layers_to_edit


        # ind = np.argsort(-proj, axis=-1)
        # attribute_tok_rank = np.where(ind == attribute_tok)[0][0]
        # attribute_tok_score = proj[ind[attribute_tok_rank]]
        # top_k_preds = [decode_tokens(tok, [i])[0] for i in ind[:k]]

        # if ix == 7 or ix == 8 or ix == 9:
        #     print('ix: ', ix, '  top_k_preds: ', top_k_preds)

# project attention and mlp to vocab

# Method
def set_act_get_hooks(model, tok_index, attn=False, attn_out=False, mlp=False, mlp_coef=False):  # mlp
    """
    Works for GPT-J, GPT2 and LLaMA
    """

    for attr in ["activations_"]:
        if not hasattr(model, attr):
            setattr(model, attr, {})

    def get_activation(name):
        def hook(module, input, output):
            if "m_coef" in name:
                # num_tokens = list(input[0].size())[1]  # (batch, sequence, hidden_state)
                model.activations_[name] = input[0][:, tok_index].detach()
            elif "m_out" in name:
                # print('m_out[0].shape: ',output[0].shape)
                model.activations_[name] = output[0][tok_index].detach()

        return hook

    hooks = []
    if "gpt" in model.config.model_type:
        for i in range(model.config.n_layer):
            if mlp_coef is True:
                hooks.append(model.transformer.h[i].mlp.fc_out.register_forward_hook(get_activation("m_coef_" + str(i))))  # gpt-j fc_out
            if mlp is True:
                hooks.append(model.transformer.h[i].mlp.register_forward_hook(get_activation("m_out_" + str(i))))
    elif "llama" in model.config.model_type:
        for i in range(model.config.num_hidden_layers):
            if mlp_coef is True:  # co-effciency
                hooks.append(model.model.layers[i].mlp.down_proj.register_forward_hook(get_activation("m_coef_" + str(i))))
            if mlp is True:
                hooks.append(model.model.layers[i].mlp.register_forward_hook(get_activation("m_out_" + str(i))))

    return hooks


# Always remove your hooks, otherwise things will get messy.
def remove_hooks(hooks):
    for hook in hooks:
        hook.remove()