import trimesh


def decimate_mesh(mesh: trimesh.Trimesh, decimate_ratio: float = 0.1) -> trimesh.Trimesh:
    """
    Simplifies mesh complexity using Quadric Error Metric decimation.
    
    Args:
        mesh: trimesh.Trimesh object
        decimate_ratio: Target face ratio (0.1 reduces mesh to 10% of original face count)
        
    Returns:
        A new simplified trimesh.Trimesh object.
    """
    if decimate_ratio >= 1.0 or decimate_ratio <= 0.0:
        return mesh.copy()
        
    # Calculate target face count from ratio
    target_faces = max(4, int(len(mesh.faces) * decimate_ratio))
    decimated = mesh.simplify_quadric_decimation(face_count=target_faces)
    return decimated
