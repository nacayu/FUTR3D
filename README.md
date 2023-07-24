# FUTR3D: A Unified Sensor Fusion Framework for 3D Detection


Official code link: [https://github.com/Tsinghua-MARS-Lab/futr3d](https://github.com/Tsinghua-MARS-Lab/futr3d)

This repo implements the paper FUTR3D: A Unified Sensor Fusion Framework for 3D Detection. [Paper](https://arxiv.org/abs/2203.10642) - [project page](https://tsinghua-mars-lab.github.io/futr3d/)

## Environment
### Prerequisite
<ol>
<li> mmcv-full>=1.3.8, <=1.4.0 </li>
<li> mmdet>=2.14.0, <=3.0.0</li>
<li> mmseg>=0.14.1, <=1.0.0</li>
<li> mmdetection3d, >=v0.17.0</li>
<li> nuscenes-devkit</li>
</ol>

### Recommended


- mmcv-full                            1.4.0
- mmdet                                2.14.0
- mmdet3d                              0.17.1
- mmsegmentation                       0.14.1

### Enviroment config

```shell
conda create -n open-mmlab python=3.8 -y
conda activate open-mmlab

pip install torch==1.9.1+cu111 torchvision==0.10.1+cu111 torchaudio==0.9.1 -f https://download.pytorch.org/whl/torch_stable.html

pip install mmcv-full==1.4.0

pip install mmdet==2.14.0
pip install mmsegmentation==0.14.1

git clone https://github.com/open-mmlab/mmdetection3d.git
cd mmdetection3d
git checkout v0.17.1 # Other versions may not be compatible.
pip install -e .


git clone https://github.com/nacayu/FUTR3D
```

### Data

For cameras with Radar setting, you should generate a meta file or say `.pkl` file including Radar infos.

```python:
bash tools/create_data.sh nuscenes v1.0-trainval 4
```

For others, please follow the mmdet3d to process the data. https://mmdetection3d.readthedocs.io/en/stable/datasets/nuscenes_det.html


## Train

For example, If your GPU memory is about 10GB, to train  small FUTR3D with Radar only on 2 GPUs, please use

```
bash tools/dist_train.sh plugin/futr3d/configs/cam_radar/res101_radar_small.py 2
```
or 

Train  full FUTR3D from official (RTX 3090: 24GB GPU) with Radar only on 2 GPUs, please use

```
bash tools/dist_train.sh plugin/futr3d/configs/cam_radar/res101_radar_large.py 2
```

## Evaluate

For example, to evalaute FUTR3D with Radar-cam on 2 GPUs, please use

```
bash tools/dist_test.sh ./plugin/futr3d/configs/cam_radar/res101_radar_large.py ./ckpts/cam_res101_radar_900q.pth --eval bbox
```

## Visualize results(Have not tested)

You should first generate .pkl results using:
```
bash tools/dist_test.sh ./plugin/futr3d/configs/cam_radar/res101_radar_large.py ./ckpts/cam_res101_radar_900q.pth --format-only
```
to generate .pkl result files and run:
```
python tools/misc/visualize_results.py /path/to/your_config /path/to/your_config_file_of_config
```

## Results

### Cam & Radar
| models      | mAP         | NDS | Link |
| ----------- | ----------- | ----| ----- |
| [Res101 + Radar](./plugin/futr3d/configs/cam_radar/res101_radar.py)  | 35.0  | 45.9 | [model](https://drive.google.com/file/d/1TRNeHrN5mOLWrUGEE0NJ3NxdtcAR5p6Q/view?usp=share_link) |

### Cam only
The camera-only version of FUTR3D is the same as DETR3D. Please check [DETR3D](https://github.com/WangYueFt/detr3d) for detail implementation.

## Acknowledgment

For the implementation, we rely heavily on [MMCV](https://github.com/open-mmlab/mmcv), [MMDetection](https://github.com/open-mmlab/mmdetection), [MMDetection3D](https://github.com/open-mmlab/mmdetection3d), and [DETR3D](https://github.com/WangYueFt/detr3d)


## Related projects 
1. [DETR3D: 3D Object Detection from Multi-view Images via 3D-to-2D Queries](https://tsinghua-mars-lab.github.io/detr3d/)
2. [MUTR3D: A Multi-camera Tracking Framework via 3D-to-2D Queries](https://tsinghua-mars-lab.github.io/mutr3d/)
3. For more projects on Autonomous Driving, check out our Visual-Centric Autonomous Driving (VCAD) project page [webpage](https://tsinghua-mars-lab.github.io/vcad/) 


## Reference

```
@article{chen2022futr3d,
  title={FUTR3D: A Unified Sensor Fusion Framework for 3D Detection},
  author={Chen, Xuanyao and Zhang, Tianyuan and Wang, Yue and Wang, Yilun and Zhao, Hang},
  journal={arXiv preprint arXiv:2203.10642},
  year={2022}
}
```

Contact: Xuanyao Chen at: `xuanyaochen19@fudan.edu.cn` or `ixyaochen@gmail.com`