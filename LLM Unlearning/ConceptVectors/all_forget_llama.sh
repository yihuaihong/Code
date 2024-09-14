#!/bin/bash

# 循环调用程序，传递不同的次序参数

#Testing on ConceptVectors Test set of LLaMA
for i in 26  #18 26 27  #{0..9} {0..94}  27 38 49
do
     python forget.py order=$i batch_size=4 gradient_accumulation_steps=8 num_epochs=1 gradient_checkpointing=True lr=1e-2 forget_loss=dpo ft_type=Full set=test
done

