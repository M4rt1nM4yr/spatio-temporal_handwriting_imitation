# Spatio-Temporal Handwriting Imitation

![Pipeline Overview](pipeline.png)

Paper Link: https://arxiv.org/abs/2003.10593

## Abstract:

>Most people think that their handwriting is unique and cannot be imitated by machines, especially not using completely new content. 
Current cursive handwriting synthesis is visually limited or needs user interaction.
We show that subdividing the process into smaller subtasks makes it possible to imitate someone's handwriting with a high chance to be visually indistinguishable for humans.
Therefore, a given handwritten sample will be used as the target style. 
This sample is transferred to an online sequence. Then, a method for online handwriting synthesis is used to produce a new realistic-looking text primed with the online input sequence. This new text is then rendered and style-adapted to the input pen. We show the effectiveness of the pipeline by generating in- and out-of-vocabulary handwritten samples that are validated in a comprehensive user study. Additionally, we show that also a typical writer identification system can partially be fooled by the created fake handwritings.

tldr: Imitating someone's handwriting by converting it to the temporal domain and back again

## Requirements

See requirements.txt

## Run the full pipeline

Before running the pipeline the trained model checkpoints have to be copied into the folder _checkpoints_ from https://drive.google.com/open?id=11fc8b7QTSqL8oIjs7ddGutlRKEL8NBqh.
To run the pipeline see __demo.sh__. 


## Code contribution

The code was mainly produced by https://github.com/Finomnis

## External sources

Link: https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix
Link: https://github.com/sjvasquez/handwriting-synthesis

