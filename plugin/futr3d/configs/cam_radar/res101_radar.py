_base_ = [
    '../_base_/datasets/nus-3d.py',
    '../_base_/default_runtime.py'
]
plugin=True
plugin_dir='plugin/futr3d/'

point_cloud_range = [-51.2, -51.2, -5.0, 51.2, 51.2, 3.0]
voxel_size = [0.2, 0.2, 8]

img_norm_cfg = dict(
    mean=[103.530, 116.280, 123.675], std=[1.0, 1.0, 1.0], to_rgb=True)

class_names = [
    'car', 'truck', 'construction_vehicle', 'bus', 'trailer', 'barrier',
    'motorcycle', 'bicycle', 'pedestrian', 'traffic_cone'
]

input_modality = dict(
    use_lidar=True,
    use_camera=True,
    use_radar=True,
    use_map=False,
    use_external=False)

model = dict(
    type='FUTR3D',
    use_LiDAR=False,
    use_Cam=True,
    use_Radar=True,
    use_grid_mask=False, # use grid mask
    img_backbone=dict(
        type='ResNet',
        depth=101,
        num_stages=4,
        out_indices=(3,),
        frozen_stages=1,
        norm_cfg=dict(type='BN2d', requires_grad=False),
        norm_eval=True,
        style='caffe',
        with_cp=True, # using checkpoint to save GPU memory
        dcn=dict(type='DCNv2', deform_groups=1, fallback_on_stride=False), # original DCNv2 will print log when perform load_state_dict
        stage_with_dcn=(False, False, True, True)),
    img_neck=dict(
        type='FPN',
        in_channels=[2048],
        out_channels=256,
        start_level=0,
        add_extra_convs='on_output',
        num_outs=1,
        relu_before_extra_convs=True),
    radar_encoder=dict(
        type='RadarPointEncoder',
        in_channels=13,
        out_channels=[32, 32, 64],
        norm_cfg=dict(type='BN1d', eps=1e-3, momentum=0.01),),
    pts_bbox_head=dict(
        type='DeformableFUTR3DHead',
        num_query=400,
        num_classes=10,
        in_channels=256,
        sync_cls_avg_factor=True,
        with_box_refine=False,
        as_two_stage=False,
        transformer=dict(
            type='FUTR3DTransformer',
            decoder=dict(
                type='FUTR3DTransformerDecoder',
                num_layers=2,
                return_intermediate=True,
                transformerlayers=dict(
                    type='DetrTransformerDecoderLayer',
                    attn_cfgs=[
                        dict(
                            type='MultiheadAttention',
                            embed_dims=256,
                            num_heads=4,
                            dropout=0.1),
                        dict(
                            type='FUTR3DCrossAtten',
                            use_LiDAR=False,
                            use_Cam=True,
                            use_Radar=True,
                            pc_range=point_cloud_range,
                            num_points=1,
                            embed_dims=256,
                            radar_topk=15,
                            radar_dims=64, )
                    ],
                    feedforward_channels=512,
                    ffn_dropout=0.1,
                    operation_order=('self_attn', 'norm', 'cross_attn', 'norm',
                                     'ffn', 'norm')))),
        bbox_coder=dict(
            type='NMSFreeCoder',
            post_center_range=[-61.2, -61.2, -10.0, 61.2, 61.2, 10.0],
            pc_range=point_cloud_range,
            max_num=300,
            voxel_size=voxel_size,
            num_classes=10),
        positional_encoding=dict(
            type='SinePositionalEncoding',
            num_feats=128,
            normalize=True,
            offset=-0.5),
        loss_cls=dict(
            type='FocalLoss',
            use_sigmoid=True,
            gamma=2.0,
            alpha=0.25,
            loss_weight=2.0),
        loss_bbox=dict(type='L1Loss', loss_weight=0.25),
        loss_iou=dict(type='IoULoss', loss_weight=0.0)),
    # model training and testing settings
        train_cfg=dict(pts=dict(
        out_size_factor=4,
        assigner=dict(
            type='HungarianAssigner3D',
            cls_cost=dict(type='FocalLossCost', weight=2.0),
            reg_cost=dict(type='BBox3DL1Cost', weight=0.25),
            iou_cost=dict(type='IoUCost', weight=0.0), # Fake cost. This is just to make it compatible with DETR head. 
        ))))

dataset_type = 'NuScenesDatasetRadar'
data_root = 'data/nuscenes/'

file_client_args = dict(backend='disk')

# x y z rcs vx_comp vy_comp x_rms y_rms vx_rms vy_rms
radar_use_dims = [0, 1, 2, 5, 6, 7, 8, 9, 12, 13, 16, 17, 18]

train_pipeline = [
    dict(
        type='LoadRadarPointsMultiSweeps',
        load_dim=18,
        sweeps_num=4,
        use_dim=radar_use_dims,
        max_num=400, ),
    dict(type='LoadMultiViewImageFromFiles'),
    dict(type='LoadAnnotations3D', with_bbox_3d=True, with_label_3d=True),
    dict(type='ObjectRangeFilter', point_cloud_range=point_cloud_range),
    dict(type='ObjectNameFilter', classes=class_names),
    dict(type='NormalizeMultiviewImage', **img_norm_cfg),
    dict(type='PadMultiViewImage', size_divisor=32),
    dict(type='DefaultFormatBundle3D', class_names=class_names),
    dict(type='Collect3D', keys=['gt_bboxes_3d', 'gt_labels_3d', 'img', 'radar'])
]

eval_pipeline = [
    dict(
        type='LoadRadarPointsMultiSweeps',
        load_dim=18,
        use_dim=radar_use_dims,
        sweeps_num=4,
        max_num=400, ),
    dict(type='LoadMultiViewImageFromFiles'),
    dict(type='NormalizeMultiviewImage', **img_norm_cfg),
    dict(type='PadMultiViewImage', size_divisor=32),
    dict(
        type='MultiScaleFlipAug3D',
        img_scale=(1333, 800),
        pts_scale_ratio=1,
        flip=False,
        transforms=[
            dict(
                type='DefaultFormatBundle3D',
                class_names=class_names,
                with_label=False),
            dict(type='Collect3D', keys=['img', 'radar'])
        ])
]

data = dict(
    samples_per_gpu=1,
    workers_per_gpu=4,
    train=dict(
        # type='CBGSDataset',
        # dataset=dict(
            type=dataset_type,
            data_root=data_root,
            ann_file=data_root + 'nuscenes_infos_train_radar.pkl',
            pipeline=train_pipeline,
            classes=class_names,
            modality=input_modality,
            test_mode=False,
            use_valid_flag=True,
            # we use box_type_3d='LiDAR' in kitti and nuscenes dataset
            # and box_type_3d='Depth' in sunrgbd and scannet dataset.
            box_type_3d='LiDAR'),
    # ),
    val=dict(
            type=dataset_type,
            pipeline=eval_pipeline, classes=class_names, modality=input_modality,
            ann_file=data_root + 'nuscenes_infos_val_radar.pkl',),
    test=dict(
            type=dataset_type,
            pipeline=eval_pipeline, classes=class_names, modality=input_modality,
            ann_file=data_root + 'nuscenes_infos_val_radar.pkl',),)

# optimizer
optimizer = dict(
    type='AdamW', 
    lr=2e-4,
    paramwise_cfg=dict(
        custom_keys={
            'img_backbone': dict(lr_mult=0.1),
        }),
    weight_decay=0.01)

optimizer_config = dict(grad_clip=dict(max_norm=35, norm_type=2))

# learning policy
lr_config = dict(
    policy='CosineAnnealing',
    warmup='linear',
    warmup_iters=500,
    warmup_ratio=1.0 / 3,
    min_lr_ratio=1e-3)

log_config = dict(
    interval=50,
    hooks=[
        dict(type='TextLoggerHook'),
        dict(type='TensorboardLoggerHook')
    ])

total_epochs = 24

evaluation = dict(interval=2, pipeline=eval_pipeline)

runner = dict(type='EpochBasedRunner', max_epochs=total_epochs)

find_unused_parameters = False

load_from = 'ckpts/cam_res101_radar_900q.pth'

fp16 = dict(loss_scale=512.)