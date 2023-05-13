from PIL import Image

i=0
file_name = 'ARGB_GT/'+str(i)+'.png'
img = Image.open(file_name)

width, height = img.size
pixel_matrix_channel_0 = []
for y in range(height):
    row = []
    for x in range(width):
        pixel = img.getpixel((x, y))[3]
        row.append(pixel)
    pixel_matrix_channel_0.append(row)
print(pixel_matrix_channel_0[0][0])



# 打开BMP图片
# for i in range(47):
#     file_name = 'ARGB_GT/'+str(i)+'.png'
#     img = Image.open(file_name)

#     width, height = img.size
#     pixel_matrix_channel_0 = []
#     for y in range(height):
#         row = []
#         for x in range(width):
#             pixel = img.getpixel((x, y))[0]
#             row.append(pixel)
#         pixel_matrix_channel_0.append(row)

#     pixel_matrix_channel_1 = []
#     for y in range(height):
#         row = []
#         for x in range(width):
#             pixel = img.getpixel((x, y))[1]
#             row.append(pixel)
#         pixel_matrix_channel_1.append(row)

#     pixel_matrix_channel_2 = []
#     for y in range(height):
#         row = []
#         for x in range(width):
#             pixel = img.getpixel((x, y))[2]
#             row.append(pixel)
#         pixel_matrix_channel_2.append(row)

#     pixel_matrix_channel_3 = []
#     for y in range(height):
#         row = []
#         for x in range(width):
#             pixel = img.getpixel((x, y))[3]
#             row.append(pixel)
#         pixel_matrix_channel_3.append(row)

# # 获取图片大小
# width, height = img.size
# print(width, height)
# # # 转化为像素矩阵
# pixel_matrix_channel_0 = []
# for y in range(height):
#     row = []
#     for x in range(width):
#         pixel = img.getpixel((x, y))[0]
#         row.append(pixel)
#     pixel_matrix_channel_0.append(row)

# pixel_matrix_channel_1 = []
# for y in range(height):
#     row = []
#     for x in range(width):
#         pixel = img.getpixel((x, y))[1]
#         row.append(pixel)
#     pixel_matrix_channel_1.append(row)

# pixel_matrix_channel_2 = []
# for y in range(height):
#     row = []
#     for x in range(width):
#         pixel = img.getpixel((x, y))[2]
#         row.append(pixel)
#     pixel_matrix_channel_2.append(row)

# pixel_matrix_channel_3 = []
# for y in range(height):
#     row = []
#     for x in range(width):
#         pixel = img.getpixel((x, y))[3]
#         row.append(pixel)
#     pixel_matrix_channel_3.append(row)
# pixel_matrix = [[],[],[],[]]
# for i in range(4):
#     pixel_matrix[i].append(1)
# print(pixel_matrix)
# a1=[1]
# a2=[2]
# a=[a1,a2]
# print(a)
# for slice in a:
#     print(slice)
# print(int('',2))