import numpy as np
import read_skeleton
import open3d as o3d
from scipy import interpolate, signal
from matplotlib import pyplot as plt


def fit_curve(points, samples=10, order=3):

    # Sort our points by Z
    points = points[np.argsort(points[:, 2])]

    #plt.plot(np.arange(len(points)), points[:, 2])
    #plt.show()

    # Downsample
    t = np.arange(len(points))
    u = np.linspace(t.min(), t.max(), samples)
    xspl = interpolate.UnivariateSpline(t, points[:, 0], k=order)
    yspl = interpolate.UnivariateSpline(t, points[:, 1], k=order)
    zspl = interpolate.UnivariateSpline(t, points[:, 2], k=order)
    down = np.array(list(zip(xspl(u), yspl(u), zspl(u))))

    #Interpolate
    t = np.arange(len(down))
    u = np.linspace(t.min(), t.max(), 2000)
    xspl = interpolate.UnivariateSpline(t, down[:, 0], k=order)
    yspl = interpolate.UnivariateSpline(t, down[:, 1], k=order)
    zspl = interpolate.UnivariateSpline(t, down[:, 2], k=order)
    interp = np.array(list(zip(xspl(u), yspl(u), zspl(u))))

    # Calculate velocity vectors
    vel = np.diff(interp, axis=0)

    # Calculate the accleration vectors
    acc = np.diff(vel, axis=0)

    # Resize Data
    interp = interp[:-2, :]
    vel = vel[:-1, :]

    # Orientation normal vector
    un = []
    for i in range(0, len(acc)):
        vn = vel[i, :]/np.linalg.norm(vel[i, :])
        an = acc[i, :]/np.linalg.norm(acc[i, :])
        uni = an - np.dot(an, vn)*vn
        uni = uni/np.linalg.norm(uni)
        un.append(uni)
    un = np.array(un)

    return interp, vel, acc, un


def calc_radius(mesh, scene, location, vector):

    # Cast the ray into the mesh and extract triangle ID
    tensor = list(location) + (list(vector))
    ray = o3d.core.Tensor([tensor], dtype=o3d.core.Dtype.Float32)
    ans = scene.cast_rays(ray)
    t_hit = ans["t_hit"].numpy()[0]

    return t_hit

def conformal_helix(mesh, points, velocity, acceleration, orientation, phi_0, freq, offset, pitch=25, dir=1):

    # Create a scene for ray casting onto the mesh
    scene = o3d.t.geometry.RaycastingScene()
    mesh1 = o3d.t.geometry.TriangleMesh.from_legacy(mesh)
    mesh_id = scene.add_triangles(mesh1)

    h = []
    for i in range(len(points)):

        # Calculate helical angle at this point
        phi = phi_0 + dir*2*np.pi*(np.linalg.norm(velocity[i, :])/pitch)
        phi_0 = phi

        # Calculate radius vector
        vn = velocity[i, :]/np.linalg.norm(velocity[i, :])
        ri = orientation[i, :]*1*np.cos(phi) + np.cross(orientation[i, :], vn)*1*np.sin(phi)

        # Find conformal radius for mesh
        R = calc_radius(mesh, scene, points[i, :], ri)

        # Calculate helix point
        w = dir*2*np.cos(freq*phi)
        hi = points[i, :] + (R+offset+w)*ri

        h.append(hi)

    return np.array(h)


def main(args):

    # Read Mesh File
    mesh = o3d.io.read_triangle_mesh(args.meshfile)

    # Read Mesh Skeleton
    verts, edges = read_skeleton.main(args.skelfile)

    # Move mesh & skel to origin (root of skeleton)
    d = -verts[np.argmin(verts[:, 2])]
    verts = verts + d
    mesh.translate(d)
    o3d.io.write_triangle_mesh("LegCentered.stl", mesh)

    # Geometry for visualization
    geometry = []

    # Create o3d lineset of the skeleton
    skel = o3d.geometry.PointCloud()
    skel.points = o3d.utility.Vector3dVector(verts)
    skel.paint_uniform_color([1, 0, 0])

    # Fit splines to skeleton data
    fit_data, vel, acc, u = fit_curve(verts)
    fit = o3d.geometry.PointCloud()
    fit.points = o3d.utility.Vector3dVector(fit_data)
    fit.paint_uniform_color([0, 1, 0])

    # Generate conformal helices
    n = 8
    angles = np.linspace(0, 2*np.pi, n+1)[:-1]
    for a in angles:
        # Positive Direction
        helix_points = conformal_helix(mesh, fit_data, vel, acc, u, a, n, 5, pitch=200)
        #np.savetxt("curves/pos"+str(a)+".txt", helix_points, delimiter=" ")
        helix = o3d.geometry.PointCloud(points=o3d.utility.Vector3dVector(helix_points))
        helix.paint_uniform_color((1, 0, 0))
        geometry.append(helix)
    for a in angles:
        # Negative Direction
        helix_points = conformal_helix(mesh, fit_data, vel, acc, u, a, n, 5, pitch=200, dir=-1)
        #np.savetxt("curves/neg"+str(a)+".txt", helix_points, delimiter=" ")
        helix = o3d.geometry.PointCloud(points=o3d.utility.Vector3dVector(helix_points))
        helix.paint_uniform_color((0, 1, 0))
        geometry.append(helix)


    if True:
        # Display mesh + skeleton
        origin = o3d.geometry.TriangleMesh.create_coordinate_frame(size=100)
        mesh.compute_triangle_normals()
        geometry.append(mesh)
        o3d.visualization.draw_geometries(geometry)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Calculate medial axis from mesh file')
    parser.add_argument('meshfile', help='Mesh file. Accepts: .stl, .obj, .ply, etc')
    parser.add_argument('skelfile', help='Input .cg skeletonization text file (output from StarLab)')

    args = parser.parse_args()
    main(args)
