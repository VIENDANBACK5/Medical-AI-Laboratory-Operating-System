import trimesh
import trimesh.smoothing


def smooth_mesh(mesh: trimesh.Trimesh, iterations: int = 10) -> trimesh.Trimesh:
    """
    Applies Laplacian smoothing to the mesh vertices to remove voxel staircase artifacts.
    
    Args:
        mesh: trimesh.Trimesh object
        iterations: Number of smoothing iterations
        
    Returns:
        A new smoothed trimesh.Trimesh object.
    """
    smoothed = mesh.copy()
    if iterations > 0:
      # filter_taubin preserves mesh volume and prevents shrinkage
      trimesh.smoothing.filter_taubin(
          smoothed,
          lamb=0.5,
          nu=-0.53,
          iterations=iterations
      )
    return smoothed
