# Medical AI Research Platform for Image-to-3D Reconstruction

Medical AI Platform
│
├── Data Layer
├── AI Engine
│     ├── Segmentation
│     ├── Detection
│     ├── Registration
│     ├── Reconstruction
│     ├── Implant Generation
│     └── Future Models
│
├── Visualization Engine
├── Export Engine
├── Experiment Engine
├── Benchmark Engine
└── Research SDK

# Tổng quan

```text
                 Web Platform
                       │
         Upload CT (.dcm)
                       │
               AI Segmentation
                       │
             Interactive 3D Viewer
                       │
              Mesh Optimization
                       │
       AI Implant Recommendation
                       │
        Export STL / OBJ /PLY
                       │
            3D Printing Ready
```

Mỗi module là một bài toán Computer Vision / Graphics khác nhau.

---

# 1. Upload CT (.dcm)

## Mục tiêu

Đọc dữ liệu từ bệnh viện.

Input là

```text
Patient/

   CT0001.dcm

   CT0002.dcm

...

   CT0650.dcm
```

Một file DICOM chứa

```text
Ảnh CT

+

Thông tin bệnh nhân

+

Voxel spacing

+

Window

+

Orientation

+

Metadata
```

Ví dụ

```text
512×512 pixel

650 slices

spacing

0.5×0.5×0.8 mm
```

Sau khi upload

↓

Server đọc thành

```python
volume.shape

(650,512,512)
```

Đây mới là input cho AI.

---

# 2. AI Segmentation

Đây là trái tim của AI.

Input

```text
3D CT Volume
```

Output

```text
Bone Mask
```

Ví dụ

Input

```text
████████████

████████████
```

AI

↓

Output

```text
00011111100

00011111100
```

Ở đây

0

=

background

1

=

bone

Nếu nhiều class

```text
0 background

1 femur

2 tibia

3 pelvis

4 vertebra

...
```

Các model

* nnUNet
* Swin UNETR
* MedSAM
* TotalSegmentator
* MONAI

Đây là phần Deep Learning.

---

# 3. Interactive 3D Viewer

Đây là phần frontend.

Sau segmentation ta có

```text
Mask
```

Nhưng người dùng không thể đọc nổi.

Ta biến thành

```text
3D Bone
```

Có thể

* xoay
* zoom
* đo khoảng cách
* cắt mặt phẳng

Ví dụ

```text
        Skull

      _________

    /          /

   /__________/

      rotate
```

Thường dùng

Frontend

* Three.js

Backend

* VTK
* vtk.js

Hoặc

* Cornerstone

---

## Tại sao cần bước này?

Nếu AI sai

↓

Bác sĩ phải nhìn được.

Nếu không có viewer

↓

Không ai tin AI.

---

# 4. Mesh Optimization

Sau segmentation

Ta mới có

```text
Voxel
```

Muốn in

↓

phải thành mesh.

Ví dụ

Mesh vừa tạo

```text
/\/\/\/\/\/\/

\/\/\/\/\/\/
```

Rất xấu.

Ta cần

## Smooth

Làm mịn

↓

```text
~~~~~~~~~~~~
```

---

## Hole Filling

Ví dụ

```text
█████

██ ██

█████
```

Lấp lỗ

↓

```text
█████

█████

█████
```

---

## Decimation

Ví dụ

```text
10 triệu triangle
```

↓

```text
200 nghìn triangle
```

Nhanh hơn.

---

## Normal Repair

Sửa hướng mặt.

Nếu không

↓

máy in sẽ lỗi.

---

Đây là Computer Graphics.

---

# 5. AI Implant Recommendation

Đây mới là research.

Giả sử

Bệnh nhân

```text
██████

██

██

```

bị mất

```text
██████

██

      X
```

AI phải nghĩ

"Nếu là người bình thường"

↓

"phần này nên có hình gì"

↓

Đề xuất

```text
++++++

++++++
```

Đây giống

Image Completion

nhưng

trong

3D.

Có thể dùng

* Diffusion
* Shape Completion
* PointNet++
* Mesh AutoEncoder
* Implicit Neural Representation

Đây là research rất mạnh.

---

## Nếu implant chưa hoàn hảo?

Không sao.

AI chỉ cần

"Recommend"

Kỹ sư sửa tiếp.

---

# 6. Export STL / OBJ

AI xong

↓

xuất

```text
implant.stl
```

Hoặc

```text
bone.obj
```

Đây là định dạng chuẩn.

Ví dụ

```text
Triangle 1

Triangle 2

Triangle 3

...
```

Các phần mềm CAD đều đọc được.

---

# 7. 3D Printing Ready

Đây chưa phải in.

Mà là

Kiểm tra

```text
Wall thickness

Minimum angle

Support

Watertight

Closed Mesh
```

Nếu đạt

↓

Hiển thị

```text
✓ Ready to Print
```

Nếu không

↓

Báo lỗi.

---

# Nếu là một sản phẩm AI

Thì kiến trúc software sẽ như sau

```text
                     React

                 (3D Viewer)

                      │

──────────────────── REST API ───────────────────

                      │

                  FastAPI

                      │

──────────────── AI Pipeline ────────────────

      DICOM Reader

             │

      Preprocessing

             │

      Segmentation Model

             │

      Mesh Generator

             │

      Mesh Optimizer

             │

      Implant Generator

             │

      STL Export

──────────────────────────────────────────────

             Storage

     CT / STL / Mesh / Models
```

---

# Theo góc nhìn của một researcher, module nào đáng nghiên cứu nhất?

Nếu chấm theo **độ khó**, **độ mới** và **khả năng ra paper**, mình sẽ xếp như sau:

| Module                                      | Độ khó | Mức độ nghiên cứu hiện nay                               | Tiềm năng paper |
| ------------------------------------------- | ------ | -------------------------------------------------------- | --------------- |
| **CT → Bone Segmentation**                  | ⭐⭐⭐    | Rất trưởng thành (nnU-Net, TotalSegmentator đã rất mạnh) | ⭐⭐              |
| **Bone Segmentation → Mesh Reconstruction** | ⭐⭐     | Chủ yếu là thuật toán kinh điển, ít AI                   | ⭐               |
| **Mesh Optimization**                       | ⭐⭐⭐    | Có nghiên cứu nhưng thiên về đồ họa máy tính             | ⭐⭐⭐             |
| **Mesh → CAD Conversion**                   | ⭐⭐⭐⭐⭐  | Chưa có lời giải tốt, rất nhiều thao tác vẫn thủ công    | ⭐⭐⭐⭐⭐           |
| **AI Implant Recommendation / Generation**  | ⭐⭐⭐⭐⭐  | Rất mới, đang là xu hướng                                | ⭐⭐⭐⭐⭐           |
| **CAD → 3D Printing Optimization**          | ⭐⭐⭐⭐   | Có nghiên cứu nhưng khá chuyên sâu về sản xuất           | ⭐⭐⭐⭐            |

Đây là lý do nhiều nhóm nghiên cứu hiện nay không cố tạo một mô hình segmentation tốt hơn 1–2% Dice, mà chuyển sang giải quyết **các mắt xích phía sau**, nơi AI vẫn chưa thay thế được con người. Nếu bạn muốn xây dựng một sản phẩm có giá trị lâu dài, hãy coi **segmentation là nền tảng**, còn **Mesh → CAD → Implant** mới là "động cơ nghiên cứu" của hệ thống. Đây cũng là nơi bạn có thể tạo ra đóng góp mới thay vì chỉ lặp lại các mô hình đã có.
