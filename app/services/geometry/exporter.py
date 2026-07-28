import trimesh


def export_mesh(mesh: trimesh.Trimesh, file_path: str, file_type: str = "stl") -> None:
    """
    Exports a 3D trimesh object to disk in the specified mesh file format.
    
    Args:
        mesh: trimesh.Trimesh object
        file_path: Output file path on disk
        file_type: Format extension, e.g., 'stl', 'obj', 'ply'
    """
    # trimesh handles writing and internal geometry structuring automatically
    mesh.export(file_path, file_type=file_type)
