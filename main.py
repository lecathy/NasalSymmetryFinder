from nasal_sym import DorsumSymmetryFinder

d = DorsumSymmetryFinder(image_path='head3d_Zach.stl', avg_path='avg_head.stl')
d.run(color='grey')