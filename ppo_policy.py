import torch
import torch.nn as nn

# IMPORTANT: This import comes from sb3_contrib, not stable_baselines3
# Make sure you have installed sb3-contrib: pip install sb3-contrib
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy

from stable_baselines3.common.torch_layers import BaseFeaturesExtractor


class Attention1DExtractor(BaseFeaturesExtractor):
    """
    A custom feature extractor that takes a 1D observation vector
    (flattened observations) and processes it via multiple Transformer
    (self-attention) layers.

    Each dimension in the observation is treated as a separate 'token'.
    """

    def __init__(
        self, observation_space, features_dim=256, n_heads=2, n_layers=2, embed_dim=64
    ):
        """
        :param observation_space: (gym.Space) The observation space (1D).
        :param features_dim: (int) Number of final extracted features (output size).
        :param n_heads: (int) Number of attention heads in each Transformer layer.
        :param n_layers: (int) Number of TransformerEncoder layers to stack.
        :param embed_dim: (int) Internal embedding dimension for each token.
        """
        super().__init__(observation_space, features_dim)
        self.obs_dim = observation_space.shape[0]

        # Project each scalar dimension to an embed_dim
        # so that we treat each dimension as a token of size embed_dim.
        self.token_proj = nn.Linear(1, embed_dim)

        # Build a standard TransformerEncoder stack
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=n_heads,
            batch_first=True,  # (B, seq_len, embed_dim)
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=n_layers
        )

        # Final linear to get to features_dim for the policy/critic
        self.linear = nn.Linear(embed_dim, features_dim)

        self._features_dim = features_dim

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        """
        :param observations: (torch.Tensor) Observations of shape (B, obs_dim)
        :return: (torch.Tensor) extracted features of shape (B, features_dim)
        """
        # Treat each dimension as a token => shape (B, obs_dim, 1)
        x = observations.unsqueeze(-1)

        # Project 1 -> embed_dim, still shape (B, obs_dim, embed_dim)
        x = self.token_proj(x)

        # Pass through the stacked TransformerEncoder
        # output shape: (B, obs_dim, embed_dim)
        x = self.transformer_encoder(x)

        # Mean pool across the token dimension (obs_dim)
        # shape => (B, embed_dim)
        x = x.mean(dim=1)

        # Final linear projection to features_dim
        features = self.linear(x)
        return features


class CustomAttentionPolicy(MaskableActorCriticPolicy):
    """
    Policy class (actor-critic) that uses the Attention1DExtractor to get features,
    then has separate MLP heads for policy and value.
    """

    def __init__(self, observation_space, action_space, lr_schedule, **kwargs):
        super().__init__(
            observation_space,
            action_space,
            lr_schedule,
            features_extractor_class=Attention1DExtractor,
            # Adjust these arguments as desired
            features_extractor_kwargs=dict(
                features_dim=256, n_heads=2, n_layers=2, embed_dim=64
            ),
            # net_arch can be customized if you want additional MLP layers
            net_arch=[dict(pi=[128, 128, 128], vf=[32, 32])],
            **kwargs,
        )

    def _build_mlp_extractor(self) -> None:
        """
        Overwrite the default MlpExtractor if desired.
        Otherwise, the base MaskableActorCriticPolicy will build a standard one
        from net_arch.
        """
        super()._build_mlp_extractor()
