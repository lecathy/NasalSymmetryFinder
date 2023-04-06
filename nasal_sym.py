import numpy as np
from stl import mesh as stl_mesh
import open3d as o3d
import trimesh
from vedo import *
from typing import List, Tuple

class DorsumSymmetryFinder:
    def __init__(self, image_path: str, avg_path: str):
        self.image_path = image_path
        self.avg_path = avg_path
        self.point_cloud = []
        self.vertices = []
        self.faces = []

    
    def icp(self) -> List[List[float]]:
        stl_image = stl_mesh.Mesh.from_file(self.image_path)
        verts = np.asarray(stl_image.vectors)

        for poly in verts:
            poly[:, [2, 1]] = poly[:, [1, 2]]
            poly[:, 1] *= -1

        nosetip = verts.reshape(-1,3)[np.argmin(verts[:,:,1].reshape(-1))]

        for poly in verts:
            poly[:, 0] -= nosetip[0]
            poly[:, 1] -= nosetip[1]
            poly[:, 2] -= nosetip[2]

        y_midpoint = (verts[:,:,1].reshape(-1)[np.argmin(verts[:,:,1].reshape(-1))] + verts[:,:,1].reshape(-1)[np.argmax(verts[:,:,1].reshape(-1))]) / 2
        cropped_verts = np.asarray([poly for poly in verts[:] if np.all(poly[:, 1] <= y_midpoint)])

        h_radius = 60
        z_radius = 95

        cropped_oval = np.asarray([poly for poly in cropped_verts[:] if np.all((poly[:, 0] ** 2 / h_radius ** 2 + poly[:, 2] ** 2 / z_radius ** 2) <= 1)])

        oval_x1 = -20
        oval_x2 = 20
        oval_z1 = -15
        oval_z2 = 42

        nose_only = np.asarray([poly for poly in cropped_oval[:] if np.all(poly[:, 0] >= oval_x1) & np.all(poly[:, 0] <= oval_x2) & np.all(poly[:, 2] >= oval_z1) & np.all(poly[:, 2] <= oval_z2)])

        avg_image = stl_mesh.Mesh.from_file(self.avg_path)
        avg_verts = avg_image.vectors

        for poly in avg_verts:
            poly[:, [2, 1]] = poly[:, [1, 2]]
            poly[:, 1] *= -1

        nosetip_avg = avg_verts.reshape(-1,3)[np.argmin(avg_verts[:,:,1].reshape(-1))]

        for poly in avg_verts:
            poly[:, 0] -= nosetip_avg[0]
            poly[:, 1] -= nosetip_avg[1]
            poly[:, 2] -= nosetip_avg[2]

        cropped_avg_nose = np.asarray([poly for poly in avg_verts[:] if np.all(poly[:, 0] <= oval_x1) | np.all(poly[:, 0] >= oval_x2) | np.all(poly[:, 2] <= oval_z1) | np.all(poly[:, 2] >= oval_z2)])

        cropped_nose_pcd = o3d.geometry.PointCloud()
        cropped_nose_pcd.points = o3d.utility.Vector3dVector(nose_only.reshape(-1,3))

        cropped_avg_nose_pcd = o3d.geometry.PointCloud()
        cropped_avg_nose_pcd.points = o3d.utility.Vector3dVector(np.asarray(cropped_avg_nose.reshape(-1,3)))
        icp = o3d.pipelines.registration.registration_icp(cropped_nose_pcd, cropped_avg_nose_pcd, 0.001)

        new_cropped_nose_pcd = cropped_nose_pcd.transform(icp.transformation)
        new_cropped_nose = np.reshape(new_cropped_nose_pcd.points, (-1,3,3))

        self.point_cloud = new_cropped_nose
        self.build_veto_mesh()
        return new_cropped_nose
    
    
    def build_veto_mesh(self) -> Tuple[List[float], List[int]]:
        if self.point_cloud is None:
            return 
        vertices = []
        faces = []

        i = 0
        for triangle in self.point_cloud:
            p1, p2, p3 = triangle
            vertices.append(p1)
            vertices.append(p2)
            vertices.append(p3)
            faces.append([i, i+1, i+2])
            i += 3
        self.vertices = vertices
        self.faces = faces
        return vertices, faces


    def find_dorsum(self) -> List[float]:
        my_trimesh = trimesh.Trimesh(vertices=self.vertices, faces=self.faces)
        dorsum = []

        heights = [i for i in range(42 + 15)]
        cross_sections = my_trimesh.section_multiplane(plane_origin=[0, 0, -15], plane_normal=[0, 0, 1], heights=heights)
        for i, cs in enumerate(cross_sections):
            if cs is not None:
                x = list(map((lambda v: v[0]), cs.vertices))
                y = list(map((lambda v: v[1]), cs.vertices))
                min_y = 1000
                min_co = -1
                for j, point in enumerate(y):
                    if point < min_y:
                        min_y = point
                        min_co = j
                dorsum.append([x[min_co], y[min_co], i-15])
        
        return dorsum
    
    def generate_2d_plots(self, shape: Mesh, spline: Mesh) -> None:
        def rotate_and_screenshot(x=None, y=None, z=None, filename=''):
            if x is not None:
                shape.rotate_x(x)
                spline.rotate_x(x)
            if y is not None:
                shape.rotate_y(y)
                spline.rotate_y(y)
            if z is not None:
                shape.rotate_z(z)
                spline.rotate_z(z)
            vp.show()
            screenshot("plots/" + filename)

        vp = Plotter(axes=False, offscreen=True)
        vp += shape
        vp += spline

        rotate_and_screenshot(filename='birds-eye.png')
        rotate_and_screenshot(x=-170, filename='worms-eye.png')
        rotate_and_screenshot(x=80, filename='centre.png')
        rotate_and_screenshot(y=45, filename='R-45.png')
        rotate_and_screenshot(y=45, filename='R-90.png')
        rotate_and_screenshot(y=-135, filename='L-45.png')
        rotate_and_screenshot(y=-45, filename='L-90.png')


    def run(self, color: str) -> None:
        self.icp()
        dorsum = self.find_dorsum()

        nose = Mesh([self.vertices, self.faces])
        nose.c(color).lighting('plastic')

        spline = Spline(points=dorsum, degree=3)
        spline.c("blue")
        spline.lw(5)

        self.generate_2d_plots(nose, spline)
       
