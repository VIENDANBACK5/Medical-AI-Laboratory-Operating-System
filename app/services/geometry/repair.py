import trimesh


def repair_and_verify(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """
    Cleans normals, fixes face orientations, and closes open boundaries/holes
    to make the mesh watertight for 3D printing.
    
    Args:
        mesh: trimesh.Trimesh object
        
    Returns:
        A cleaned and repaired trimesh.Trimesh object.
    """
    repaired = mesh.copy()
    
    # 1. Align/Fix face normals
    repaired.fix_normals()
    
    # 2. Fill holes on boundary edges
    repaired.fill_holes()

    # 3. Clean degenerate and duplicate triangles.
    # The legacy remove_degenerate_faces()/remove_duplicate_faces() helpers were
    # removed in trimesh 4.x; the supported path is update_faces() with a face mask.
    repaired.update_faces(repaired.nondegenerate_faces())
    repaired.update_faces(repaired.unique_faces())

    return repaired
