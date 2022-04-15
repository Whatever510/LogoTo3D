import time

import trimesh
import pyrender
import cv2
import numpy as np

from marching_cubes import run

dict_colors = {'deep_crimson': ["#120103", 0.7],
               'mercury_silver': ["#161616", 0.7],
               'abyss_blue': ["#000919", 0.6],
               'red_multicoat': ["#0a0101", 0.1],
               'solid_black': ["#020202", 1.0],
               'deep_blue': ["#000919", 0.7],
               'silver_metallic': ["#161616", 0.6],
               'pearl_white': ["#c2d0cf", 0.01],
               'midnight_silver': ["#131416", 0.8], }



def hex2rgb(hex):
    """ convert hex to rgb in range 0-1 """
    hex = hex.lstrip('#')
    hlen = len(hex)
    return tuple(int(hex[i:i + hlen // 3], 16) / 255 for i in range(0, hlen, hlen // 3))


def create_meshes(mesh_trimesh):
    """ Create a mesh object and set the material properties """
    nodes = []
    keys = list(dict_colors.keys())
    for key in keys:
        material = pyrender.MetallicRoughnessMaterial(
            metallicFactor=dict_colors[key][1],
            baseColorFactor=hex2rgb(dict_colors[key][0]),
            alphaMode='OPAQUE',
            roughnessFactor=0.4)

        mesh = pyrender.Mesh.from_trimesh(mesh_trimesh, material=material)

        node = pyrender.Node(mesh=mesh)
        nodes.append(node)
    return nodes


def create_captions_list():
    """ BROKEN: Create a list of captions for the viewer """
    captions = []
    captions.append(
        {'text': '',
         'location': pyrender.constants.TextAlign.TOP_CENTER,
         'font_name': 'fonts/Arial.ttf',
         'font_pt': 20,
         'color': (0, 0, 0, 255),
         'scale': 1
         })
    return captions


def get_flags():
    """ Get the flags for the viewer """
    render_flags = {
        'flip_wireframe': False,
        'all_wireframe': False,
        'all_solid': False,
        'shadows': False,
        'vertex_normals': False,
        'face_normals': False,
        'cull_faces': True,
        'cull_backfaces': True,
    }

    viewer_flags = {
        'mouse_pressed': False,
        'rotate': True,
        'rotate_rate': np.pi / 6.0,
        'rotate_axis': np.array([1.0, 0.0, 0.0]),
        'record': False,
        'use_raymond_lighting': True,
        'use_direct_lighting': False,
        'lighting_intensity': 3.0,
        'use_perspective_cam': True,
        'save_directory': '',
        'window_title': 'Tesla Logo',
        'refresh_rate': 15.0,
        'fullscreen': False,
        'show_world_axis': False,
        'show_mesh_axes': False,
        'caption': [],
    }

    return viewer_flags, render_flags


def render(mesh_trimesh):
    """ Render the mesh """
    viewer_flags, render_flags = get_flags()

    keys = list(dict_colors.keys())

    nodes = create_meshes(mesh_trimesh)

    scene = pyrender.Scene(ambient_light=(0.5, 0.5, 0.5), bg_color=(0.1, 0.1, 0.1))

    scene.add_node(nodes[0])

    light = pyrender.DirectionalLight(color=[0.8, 0.8, 0.8], intensity=1)
    light_pose = np.eye(4)

    light_pose[:3, 3] = np.array([0, -1, 1])
    scene.add(light, pose=light_pose)

    # Create a renderer
    v = pyrender.Viewer(scene, run_in_thread=True, viewer_flags=viewer_flags, render_flags=render_flags)

    start = time.time()
    counter = 0
    while True:
        if time.time() - start > 8:

            start = time.time()
            v.render_lock.acquire()
            scene.remove_node(nodes[counter])
            counter += 1
            if counter == len(nodes):
                counter = 0
            print(keys[counter])
            # @ TODO solve caption issue
            #v.viewer_flags["caption"][0]["text"] = keys[counter]
            node = nodes[counter]
            # @ TODO solve rotation issue -> camera should look at the center of the object
            # node.rotation = np.array([ 0,-0.2334454, 0, 0.9723699])
            # node.translation = np.array([30, 0, 0])
            scene.add_node(node)
            v.render_lock.release()
        else:
            v.render_lock.acquire()
            v.render_lock.release()


def main():
    points_3d, triangles, normals = run()
    # Create a mesh object

    mesh_trimesh = trimesh.Trimesh(vertices=points_3d, faces=triangles, normals=normals)

    render(mesh_trimesh)


if __name__ == "__main__":
    main()
