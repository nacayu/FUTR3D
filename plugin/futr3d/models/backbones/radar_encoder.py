import torch
from mmcv.cnn import build_norm_layer
from mmcv.runner import auto_fp16
from torch import nn
from torch.nn import functional as F

from mmcv.utils import Registry
RADAR_ENCODERS = Registry('radar_encoder')

def build_radar_encoder(cfg):
    """Build backbone."""
    return RADAR_ENCODERS.build(cfg)


class RFELayer(nn.Module):
    """Radar Feature Encoder layer.
    Args:
        in_channels (int): Number of input channels.
        out_channels (int): Number of output channels.
        norm_cfg (dict): Config dict of normalization layers
    """

    def __init__(self,
                 in_channels,
                 out_channels,
                 norm_cfg=dict(type='BN1d', eps=1e-3, momentum=0.01),
                 ):
        super(RFELayer, self).__init__()
        self.fp16_enabled = False
        self.norm = build_norm_layer(norm_cfg, out_channels)[1]
        self.linear = nn.Linear(in_channels, out_channels, bias=False)

    def forward(self, inputs):
        """Forward function.
        Args:
            inputs (torch.Tensor): Points features of shape (B, M, C).
                M is the number of points in
                C is the number of channels of point features.
        Returns:
            the same shape
        """
        
        x = self.linear(inputs) # [B, M, C]
        # BMC -> BCM -> BMC
        x = self.norm(x.permute(0, 2, 1).contiguous()).permute(0, 2,
                                                               1).contiguous()
        out = F.relu(x)

        return out


@RADAR_ENCODERS.register_module()
class RadarPointEncoder(nn.Module):

    def __init__(self,
                in_channels, 
                out_channels, 
                norm_cfg=dict(type='BN1d', eps=1e-3, momentum=0.01), 
                ):
        super(RadarPointEncoder, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        in_chn = in_channels

        layers = []
        for out_chn in out_channels:
            layer = RFELayer(in_chn, out_chn)
            layers.append(layer)
            in_chn = out_chn
        self.feat_layers = nn.Sequential(*layers)
        self.fp16_enabled = False
    
    @auto_fp16(apply_to=('points'))
    def forward(self, points):
        '''
        points: [B, N, C]. N: as max
        masks: [B, N, 1]
        ret: 
            out: [B, N, C+1], last channel as 0-1 mask
        '''
        masks = points[:, :, [-1]]
        x = points[:, :, :-1]
        xy = points[:, :, :2]
        
        for feat_layer in self.feat_layers:
            x = feat_layer(x)
        
        out = x * masks
        out = torch.cat((x, masks), dim=-1)
        out = torch.cat((xy, out), dim=-1)
        return out