"""
This code has largely been made available by https://huggingface.co/ai-lab/ESGify
"""

from collections import OrderedDict

import torch
from transformers import MPNetPreTrainedModel, MPNetModel


# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


# Definition of ESGify class because of custom, sentence-transformers like, mean pooling function and classifier head
class ESGify(MPNetPreTrainedModel):
    """Model for Classification ESG risks from text."""

    def __init__(self, config):  # tuning only the head
        """
        """
        super().__init__(config)
        # Instantiate Parts of model
        self.mpnet = MPNetModel(config, add_pooling_layer=False)
        self.id2label = config.id2label
        self.label2id = config.label2id
        self.classifier = torch.nn.Sequential(OrderedDict([('norm', torch.nn.BatchNorm1d(768)),
                                                           ('linear', torch.nn.Linear(768, 512)),
                                                           ('act', torch.nn.ReLU()),
                                                           ('batch_n', torch.nn.BatchNorm1d(512)),
                                                           ('drop_class', torch.nn.Dropout(0.2)),
                                                           ('class_l', torch.nn.Linear(512, 47))]))

    def forward(self, input_ids, attention_mask):
        # Feed input to mpnet model
        outputs = self.mpnet(input_ids=input_ids,
                             attention_mask=attention_mask)

        # Mean pooling dataset and eed input to classifier to compute logits
        logits = self.classifier(mean_pooling(outputs['last_hidden_state'], attention_mask))

        # Apply sigmoid
        logits = 1.0 / (1.0 + torch.exp(-logits))
        return logits
