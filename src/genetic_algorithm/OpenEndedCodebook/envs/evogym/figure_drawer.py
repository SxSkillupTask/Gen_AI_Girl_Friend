import os
import pickle
import json
from gym import Env
import numpy as np
import torch

import matplotlib.pyplot as plt
from PIL import Image
import imageio
from pygifsicle import gifsicle

from gym_utils import make_vec_envs

from ppo import Policy


RenderPaddings = {
    'Walker-v0'         : ((4, 4), (1, 8)),
    'BridgeWalker-v0'   : ((4, 4), (1, 7)),
    'CaveCrawler-v0'    : ((4, 1), (1, 1)),
    'Jumper-v0'         : ((1, 1), (1, 8)),
    'Flipper-v0'        : ((4, 4), (1, 8)),
    'Balancer-v0'       : ((1, 1), (1, 4)),
    'Balancer-v1'       : ((1, 1), (1, 4)),
    'UpStepper-v0'      : ((4, 4), (1, 10)),
    'DownStepper-v0'    : ((4, 4), (1, 5)),
    'ObstacleTraverser-v0'  : ((4, 4), (1, 7)),
    'ObstacleTraverser-v1'  : ((4, 2), (1, 6)),
    'Hurdler-v0'        : ((4, 4), (1, 4)),
    'GapJumper-v0'      : ((4, 4), (1, 8)),
    'PlatformJumper-v0' : ((4, 4), (1, 8)),
    'Traverser-v0'      : ((4, 4), (1, 6)),
    'Lifter-v0'         : ((1, 1), (1, 5)),
    'Carrier-v0'        : ((4, 4), (1, 3)),
    'Carrier-v1'        : ((4, 1), (1, 3)),
    'Pusher-v0'         : ((4, 4), (1, 6)),
    'Pusher-v1'         : ((4, 4), (1, 6)),
    'BeamToppler-v0'    : ((1, 1), (1, 2)),
    'BeamSlider-v0'     : ((1, 1), (1, 2)),
    'Thrower-v0'        : ((4, 1), (1, 8)),
    'Catcher-v0'        : ((2, 2), (1, 1)),
    'AreaMaximizer-v0'  : ((1, 1), (1, 1)),
    'AreaMinimizer-v0'  : ((1, 1), (1, 1)),
    'WingspanMazimizer-v0'  : ((1, 1), (1, 1)),
    'HeightMaximizer-v0'    : ((1, 1), (1, 4)),
    'Climber-v0'        : ((1, 1), (1, 1)),
    'Climber-v1'        : ((1, 1), (1, 1)),
    'Climber-v2'        : ((1, 1), (1, 1)),
    'BidirectionalWalker-v0': ((4, 4), (1, 6)),
    'Parkour-v0'        : ((4, 4), (1, 8)),
    'Parkour-v1'        : ((4, 4), (1, 8)),
}


def pool_init_func(lock_):
    global lock
    lock = lock_


def make_gif(filename, env, viewer, controller, controller_type, padding, track=True, resolution_scale=32, deterministic=True):
    assert controller_type in ['NEAT', 'PPO']

    if track:
        resolution = (8*resolution_scale, 144/32*resolution_scale)
        viewer.set_resolution(resolution)
    else:
        grid_size = env.get_attr("world", indices=None)[0].grid_size
        view_size = (grid_size[0]+padding[0][0]+padding[0][1], grid_size[1]+padding[1][0]+padding[1][1])
        resolution = (view_size[0]*resolution_scale, view_size[1]*resolution_scale)
        camera_position = ((grid_size[0]-padding[0][0]+padding[0][1])/2, (grid_size[1]-padding[1][0]+padding[1][1])/2)

        viewer.track_objects()
        viewer.set_view_size(view_size)
        viewer.set_resolution(resolution)
        viewer.set_pos(camera_position)


    done = False
    obs = env.reset()
    imgs = []
    while not done:

        img = viewer.render(mode='img', hide_grid=False)
        imgs.append(img)

        if controller_type=='NEAT':
            action = [np.array(controller.activate(obs[0]))*2 - 1]
        elif controller_type=='PPO':
            with torch.no_grad():
                action = controller.predict(obs, deterministic=deterministic)
        else:
            return
        obs, _, done, infos = env.step(action)


    imageio.mimsave(filename, imgs, duration=(1/50.0))

    with lock:
        gifsicle(sources=filename,
                 destination=filename,
                 optimize=False,
                 colors=64,
                 options=["--optimize=3","--no-warnings"])

    return


def make_jpg(filename, env, viewer, controller, controller_type, padding, interval='timestep', resolution_scale=32, start_timestep=0, timestep_interval=80, distance_interval=0.8, blur=0, blur_temperature=0.6, display_timestep=False, draw_trajectory=False, deterministic=True):
    assert controller_type in ['NEAT', 'PPO']
    assert interval in ['timestep', 'distance']

    grid_size = env.get_attr("world", indices=None)[0].grid_size

    view_size = (grid_size[0]+padding[0][0]+padding[0][1], grid_size[1]+padding[1][0]+padding[1][1])
    resolution = (view_size[0]*resolution_scale, view_size[1]*resolution_scale)
    camera_position = ((grid_size[0]-padding[0][0]+padding[0][1])/2, (grid_size[1]-padding[1][0]+padding[1][1])/2)

    viewer.track_objects()
    viewer.set_view_size(view_size)
    viewer.set_resolution(resolution)
    viewer.set_pos(camera_position)

    obs = env.reset()

    images = []
    draw_times = []
    blur_images = {}
    position_history = []
    prev_position = None
    done = False
    while not done:

        position = env.env_method('get_pos_com_obs', object_name='robot')[0]
        position_history.append(position)
        time = env.env_method('get_time')[0]
        draw = False
        if interval=='timestep':
            if time>=start_timestep and (time-start_timestep)%timestep_interval==0:
                draw = True
                mix_value = len(images) + 3
        elif interval=='distance':
            if time>=start_timestep and np.linalg.norm(position-prev_position)>distance_interval:
                draw = True
                mix_value = len(images) + 3

        if draw:
            image = viewer.render(mode='img', hide_grid=True)
            alpha = np.where(np.mean(image, axis=-1)>240, 1e-5, 2**mix_value)
            images.append((image, np.expand_dims(alpha, axis=-1)))
            draw_times.append(time)

            prev_position = position

        elif blur>0:
            image = viewer.render(mode='img', hide_grid=True, hide_edges=True)
            blur_images[time] = image

        if controller_type=='NEAT':
            action = [np.array(controller.activate(obs[0]))*2 - 1]
        elif controller_type=='PPO':
            with torch.no_grad():
                action = controller.predict(obs, deterministic=deterministic)
        else:
            return
        obs, _, done, infos = env.step(action)

    if blur>0:
        for draw_time in draw_times:
            for diff,m in enumerate(np.linspace(0.2, 1.0, blur)[:min(blur, draw_time)]):
                time = draw_time - diff - 1
                if time in draw_times:
                    break

                image = blur_images[time]
                image = np.maximum(image, 60)
                image = image + (255-image) * m**blur_temperature
                image = np.minimum(image, 247)
                alpha = np.where(np.mean(image, axis=-1)>240, 1e-5, 1e-1)
                images.append((image, np.expand_dims(alpha, axis=-1)))

    image = sum([image*alpha for image,alpha in images]) / sum([alpha for _,alpha in images])
    image = image.astype('uint8')

    fig, ax = plt.subplots(figsize=(view_size[0]/3, view_size[1]/3), dpi=4*resolution_scale)
    ax.imshow(image)

    if display_timestep:
        for draw_time in draw_times:
            position = position_history[draw_time]
            x = (padding[0][0] + position[0]*10) * resolution_scale
            y = (padding[1][1] + grid_size[1] - position[1]*10 - 3.2) * resolution_scale
            ax.text(x,y,f't={draw_time}', ha='center', fontsize=12)

    if draw_trajectory:
        data = []
        for i,position in enumerate(position_history):
            x = (padding[0][0] + position[0]*10) * resolution_scale
            y = (padding[1][1] + grid_size[1] - position[1]*10) * resolution_scale
            data.append((x, y))

        cmap = plt.get_cmap('gist_earth')
        for i in range(len(data)-1):
            ax.plot([data[i][0],data[i+1][0]], [data[i][1],data[i+1][1]], c=cmap(int(i/len(data)*255)), linewidth=1.0, alpha=1.0, marker='None')

    ax.axis('off')
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

    return


class EvogymControllerDrawerNEAT:
    def __init__(self, save_path, env_id, robot, genome_config, decode_function, overwrite=True, save_type='gif', **draw_kwargs):
        assert save_type in ['gif', 'jpg']

        self.save_path = os.path.join(save_path, save_type)
        self.env_id = env_id
        self.robot = robot
        self.genome_config = genome_config
        self.decode_function = decode_function
        self.overwrite = overwrite
        self.save_type = save_type
        self.draw_kwargs = draw_kwargs
        self.padding = RenderPaddings[self.env_id]

        os.makedirs(self.save_path, exist_ok=True)

    def draw(self, key, genome_file, directory=''):
        save_dir = os.path.join(self.save_path, directory)
        os.makedirs(save_dir, exist_ok=True)

        filename = os.path.join(save_dir, f'{key}.{self.save_type}')
        if not self.overwrite and os.path.exists(filename):
            return

        env = make_vec_envs(self.env_id, self.robot, 0, 1, allow_early_resets=False)
        viewer = env.get_attr("default_viewer", indices=None)[0]

        with open(genome_file, 'rb') as f:
            genome = pickle.load(f)
        controller = self.decode_function(genome, self.genome_config)

        if self.save_type=='gif':
            make_gif(filename, env, viewer, controller, 'NEAT', self.padding, **self.draw_kwargs)

        elif self.save_type=='jpg':
            make_jpg(filename, env, viewer, controller, 'NEAT', self.padding, **self.draw_kwargs)

        env.close()
        print(f'genome {key} ... done')
        return


class EvogymControllerDrawerPPO:
    def __init__(self, save_path, env_id, robot, overwrite=True, save_type='gif', **draw_kwargs):
        assert save_type in ['gif', 'jpg']

        self.save_path = os.path.join(save_path, save_type)
        self.env_id = env_id
        self.robot = robot
        self.overwrite = overwrite
        self.save_type = save_type
        self.draw_kwargs = draw_kwargs
        self.padding = RenderPaddings[self.env_id]

        os.makedirs(self.save_path, exist_ok=True)

    def draw(self, iter, ppo_file, directory=''):
        save_dir = os.path.join(self.save_path, directory)
        os.makedirs(save_dir, exist_ok=True)

        filename = os.path.join(save_dir, f'{iter}.{self.save_type}')
        if not self.overwrite and os.path.exists(filename):
            return

        env = make_vec_envs(self.env_id, self.robot, 0, 1, allow_early_resets=False, vecnormalize=True)
        viewer = env.get_attr("default_viewer", indices=None)[0]


        controller = Policy(env.observation_space, env.action_space, device='cpu')
        params, obs_rms = torch.load(ppo_file)
        controller.load_state_dict(params)

        env.training = False
        env.obs_rms = obs_rms

        if self.save_type=='gif':
            make_gif(filename, env, viewer, controller, 'PPO', self.padding, **self.draw_kwargs)

        elif self.save_type=='jpg':
            make_jpg(filename, env, viewer, controller, 'PPO', self.padding, **self.draw_kwargs)

        env.close()
        print(f'iter {iter} ... done')
        return


class EvogymStructureDrawerCPPN:
    def __init__(self, save_path, env_id, overwrite=True, save_type='gif', **draw_kwargs):
        assert save_type in ['gif', 'jpg']

        self.save_path = os.path.join(save_path, save_type)
        self.env_id = env_id
        self.overwrite = overwrite
        self.save_type = save_type
        self.draw_kwargs = draw_kwargs
        self.padding = RenderPaddings[self.env_id]

        os.makedirs(self.save_path, exist_ok=True)

    def draw(self, key, robot_file, ppo_file, directory=''):
        save_dir = os.path.join(self.save_path, directory)
        os.makedirs(save_dir, exist_ok=True)

        filename = os.path.join(save_dir, f'{key}.{self.save_type}')
        if not self.overwrite and os.path.exists(filename):
            return

        robot = np.load(robot_file)

        env = make_vec_envs(self.env_id, robot, 0, 1, allow_early_resets=False, vecnormalize=True)
        viewer = env.get_attr("default_viewer", indices=None)[0]

        controller = Policy(env.observation_space, env.action_space, device='cpu')
        params, obs_rms = torch.load(ppo_file)
        controller.load_state_dict(params)

        env.training = False
        env.obs_rms = obs_rms

        if self.save_type=='gif':
            make_gif(filename, env, viewer, controller, 'PPO', self.padding, **self.draw_kwargs)

        elif self.save_type=='jpg':
            make_jpg(filename, env, viewer, controller, 'PPO', self.padding, **self.draw_kwargs)

        env.close()
        print(f'genome {key} ... done')
        return


class EvogymDrawerPOET:
    def __init__(self, env_id, save_path, robot, recurrent=False, overwrite=True, save_type='gif', **draw_kwargs):
        assert save_type in ['gif', 'jpg']

        self.save_path = os.path.join(save_path, save_type)
        self.env_id = env_id
        self.robot = robot
        self.recurrent = recurrent
        self.overwrite = overwrite
        self.save_type = save_type
        self.draw_kwargs = draw_kwargs
        self.padding = RenderPaddings[self.env_id]

        os.makedirs(self.save_path, exist_ok=True)

    def draw(self, key, terrain_file, core_file, directory=''):
        save_dir = os.path.join(self.save_path, directory)
        os.makedirs(save_dir, exist_ok=True)

        filename = os.path.join(save_dir, f'{key}.{self.save_type}')
        if not self.overwrite and os.path.exists(filename):
            return

        terrain = json.load(open(terrain_file, 'r'))
        env_kwargs = dict(**self.robot, terrain=terrain)
        env = make_vec_envs(self.env_id, env_kwargs, 0, 1, allow_early_resets=False, vecnormalize=True)
        viewer = env.get_attr("default_viewer", indices=None)[0]

        controller = Policy(env.observation_space, env.action_space, device='cpu')
        params, obs_rms = torch.load(core_file)
        controller.load_state_dict(params)

        env.training = False
        env.obs_rms = obs_rms

        if self.save_type=='gif':
            make_gif(filename, env, viewer, controller, 'PPO', self.padding, **self.draw_kwargs)

        elif self.save_type=='jpg':
            make_jpg(filename, env, viewer, controller, 'PPO', self.padding, **self.draw_kwargs)

        env.close()
        print(f'key {key} ... done')
        return