def reconstruction_pic(origin_pic):
    expand_pic = [[0 for _ in range(len(origin_pic[0])+2)] for _ in range(len(origin_pic)+1)]
    for i in range(len(origin_pic)):
        for j in range(len(origin_pic[0])):
            expand_pic[i+1][j+1]=origin_pic[i][j]
    
    for i in range(len(origin_pic)-1):
        expand_pic[i+2][0]=origin_pic[i][0]
        expand_pic[i+1][len(origin_pic[0])+1]=origin_pic[i][len(origin_pic[0])-1]
    return expand_pic

def get_pixels(expand_pic,hang_index,lie_index):
    _hang_index = hang_index+1
    _lie_index = lie_index+1

    x = expand_pic[_hang_index     ][_lie_index      ]
    a = expand_pic[_hang_index     ][_lie_index    - 1  ]
    b = expand_pic[_hang_index  -1 ][_lie_index    ]
    c = expand_pic[_hang_index - 1 ][_lie_index   -1 ]
    d = expand_pic[_hang_index -1  ][_lie_index  +1  ]
    return x,a,b,c,d

def get_gradient(a,b,c,d):
    D1 = d-b
    D2 = b-c
    D3 = c-a
    return D1,D2,D3

def mode_choose(D1,D2,D3):
    '''
    return mode = 0 : run mode
    return mode = 1 : regular mode
    '''
    if D1==0 and D2==0 and D3==0:
        mode = 0
    else:
        mode = 1
    return mode

def quantinize(D):
    if D<=-21:
        Q=-4
    elif D<=-7:
        Q=-3
    elif D<=-3:
        Q=-2
    elif D<0:
        Q=-1
    elif D==0:
        Q=0
    elif D<=3:
        Q=1
    elif D<=7:
        Q=2
    elif D<=21:
        Q=3
    else:
        Q=4
    return Q

def mapping_and_sign(Q1,Q2,Q3):
    if Q1<0 or (Q1==0 and Q2<0) or (Q1==0 and Q2==0 and Q3<0):
        SIGN = -1
        Q1,Q2,Q3=-Q1,-Q2,-Q3
    else:
        SIGN = 1
    Q = 81*Q1+9*Q2+Q3
    return Q,SIGN

def prediction(a,b,c):
    if c>max(a,b):
        Px = min(a,b)
    elif c<min(a,b):
        Px = max(a,b)
    else:
        Px = a+b-c
    return Px

def prediction_corrected(Px,SIGN,Q,MAXVAL=255):
    Px = Px + SIGN*C[Q]
    if(Px>MAXVAL):
        Px = MAXVAL
    if(Px<0):
        Px = 0
    return Px

def prediction_error(x,Px,SIGN):
    Errval = (x-Px)*SIGN
    return Errval

def prediction_error_modulo_reduction(Errval,RANGE=256):
    ### 两个条件均自行修改过
    if Errval<(-RANGE/2):
        Errval+=RANGE
    elif Errval>=((RANGE-1)/2):
        Errval-=RANGE
    return Errval

def Golomb_k(Q):
    global A,B,C,N
    k=0
    while((N[Q]<<k)<A[Q] and k<=7):
        k+=1
    return k

def error_mapping(Errval,Q,k):
    if(k==0 and 2*B[Q]<=-N[Q]):# special mapping
        if(Errval >= 0):
            MErrval = 2*Errval+1
        else:
            MErrval = -2*(Errval+1)
    else:# regular mapping
        if Errval>=0:
            MErrval = 2*Errval
        else:
            MErrval = -2*Errval-1
    # print(Errval,MErrval)
    return MErrval

def update_params(Q,Errval):
    global A,B,C,N,RESET,MAX_C,MIN_C
    B[Q] = B[Q] + Errval
    A[Q] = (A[Q] + Errval) if (Errval>=0) else (A[Q] - Errval)
    if N[Q]==RESET:
        A[Q] = A[Q] >> 1
        if B[Q] >= 0:
            B[Q] = B[Q] >> 1
        else:
            B[Q] = -((1-B[Q])>>1)
        N[Q]>>1
    N[Q]=N[Q]+1

    if B[Q]<=-N[Q]:
        B[Q]=B[Q]+N[Q]
        if C[Q]>MIN_C:
            C[Q] = C[Q] - 1
        if B[Q]<=-N[Q]:
            B[Q] = -N[Q] + 1
    elif B[Q]>0:
        B[Q] = B[Q]-N[Q]
        if C[Q] < MAX_C:
            C[Q] = C[Q]+1
        if B[Q]>0:
            B[Q]=0
            

def bin8(num):
    if(num>255):
        print("num is",num)
        raise Exception("num >255!")
    outnum = bin(num)[2:]
    while(len(outnum)!=8):
        outnum = '0' + outnum
    return outnum

def one_element_coding(num):
    outnum = '0' * num + '1'
    return outnum

def golomb_coding(MErrval,k,LIMIT=32,qbpp=8):
    MErrval_R_k = MErrval>>k
    outstr = ''
    if MErrval_R_k < LIMIT-qbpp-1:
        outstr+=one_element_coding(MErrval_R_k)
        outstr+=bin8(MErrval)[-k:]
    else:
        outstr+=one_element_coding(LIMIT-qbpp-1)
        outstr+=bin8(MErrval-1)[-qbpp:]
    return outstr

def golomb_decoding(outstr,k,LIMIT=32,qbpp=8):
    pass

def regular_mode(x,a,b,c,d):
    D1,D2,D3 = get_gradient(a,b,c,d)

    Q,SIGN = mapping_and_sign(quantinize(D1),quantinize(D2),quantinize(D3))

    Px = prediction(a,b,c)

    Px = prediction_corrected(Px,SIGN,Q)

    Errval = prediction_error(x,Px,SIGN)
    # print("in regular mode,Errval before mr is",Errval)
    Errval = prediction_error_modulo_reduction(Errval)
    # print("in regular mode,Errval after mr is",Errval)
    
    k = Golomb_k(Q)

    MErrval = error_mapping(Errval,Q,k)
    # print("in regular mode,MErrval,k is",MErrval,k)
    regular_outstream = golomb_coding(MErrval,k)

    update_params(Q,Errval)
    # print("Q A[Q] B[Q] C[Q] N[Q] is",Q,A[Q],B[Q],C[Q],N[Q])
    return regular_outstream

def GetNextSample():
    global Pixel_cnt,expand_pic,origin_pic
    i = Pixel_cnt//(len(origin_pic[0]))
    j = Pixel_cnt%(len(origin_pic[0]))
    if j==len(origin_pic[0])-1:
        EOL = 1
    else:
        EOL = 0
    x,a,b,c,d = get_pixels(expand_pic, i,j)
    Pixel_cnt +=1
    return x,a,b,c,d,i,j,EOL

def get_nextmode(i,j):
    global origin_pic,expand_pic
    Pixel_cnt = i*len(origin_pic[0])+j
    Pixel_cnt+=1
    next_i = Pixel_cnt//(len(origin_pic[0]))
    next_j = Pixel_cnt%(len(origin_pic[0]))
    next_x ,next_a,next_b,next_c,next_d = get_pixels(expand_pic, next_i,next_j)
    next_D1,next_D2,next_D3 = get_gradient(next_a,next_b,next_c,next_d)
    next_mode = mode_choose(next_D1,next_D2,next_D3)
    return next_mode

def get_nextxabcd_equal(i,j):
    ## nextisequal=1:next x=a=b=c=d
    ## nextisequal=2:next a=b=c=d!=x
    ## nextisequal=0:else
    global origin_pic,expand_pic
    Pixel_cnt = i*len(origin_pic[0])+j
    Pixel_cnt+=1
    next_i = Pixel_cnt//(len(origin_pic[0]))
    next_j = Pixel_cnt%(len(origin_pic[0]))
    _, next_a,next_b,next_c,next_d = get_pixels(expand_pic, next_i,next_j)
    nextisequal = 0
    if next_a==next_b==next_c==next_d :
        nextisequal = 1
    else:
        nextisequal = 0
    return nextisequal
def bitstream(num,width):
    if num==0:
        return ''
    else:
        num_2 = bin(num)[2:]
        if len(num_2)>width:
            raise Exception("width is not enough for num!")
        while(len(num_2)!=width):
            num_2='0'+num_2
        return num_2

def run_mode(x,a,b,c,d,EOL):
    global RUNcnt,RUNval,RUNindex
    run_outstream = ''
    RUNval = a
    while x==RUNval:
        RUNcnt+=1
        if EOL==0:
            x,a,b,c,d,i,j,EOL = GetNextSample()
        else:
            break
    # print("RUNcnt is",RUNcnt)
    # print("x,a,b,c,d,EOL is",x,a,b,c,d,EOL)

    while RUNcnt>=2**J[RUNindex] :
        run_outstream+='1'
        RUNcnt-=2**J[RUNindex]
        if RUNindex<31:
            RUNindex+=1
    # print("after decline runcnt")
    # print("RUNcnt is",RUNcnt)
    # print("RUNindex is",RUNindex)

    if(EOL==1):
        if RUNcnt>0:
            run_outstream+='1'
        return run_outstream
    
    run_outstream+='0'
    run_outstream+=bitstream(RUNcnt,J[RUNindex])
    
    run_outstream+=run_interruption_sample_encoding(x,a,b,c,d)

    if(RUNindex>0):
        RUNindex-=1
    return run_outstream

def run_interruption_sample_encoding(x,a,b,c,d):
    global A,B,C,N,Nn
    
    RItype = 1 if a == b else 0
    Px = a if RItype == 1 else b
    Errval = x - Px
    if RItype == 0 and a>b :
        Errval = -Errval
        SIGN = -1
    else:
        SIGN = 1
    
    Errval = prediction_error_modulo_reduction(Errval,RANGE)
    # print("Errval is",Errval)
    TEMP = A[365] if RItype==0 else A[366]+(N[366]>>1)
    Q=RItype+365
    
    # print("TEMP is",TEMP)
    k=0
    while((N[Q]<<k)<TEMP and k<=7):
        k+=1
    
    if k==0 and Errval>0 and 2*Nn[Q]<N[Q]:
        mapnum = 1
    elif Errval<0 and 2*Nn[Q]>=N[Q]:
        mapnum = 1
    elif Errval<0 and k!=0:
        mapnum = 1
    else:
        mapnum = 0

    EMErrval = 2*abs(Errval)-RItype-mapnum
    # print("EMErrval is",EMErrval)
    # print("k is",k)
    # print("run mode before update is A[Q] N[Q] is",A[Q],N[Q])
    run_interruption_encoding = golomb_coding(EMErrval,k,LIMIT=(LIMIT-J[RUNindex]-1))

    if Errval<0:
        Nn[Q]+=1
    A[Q]+=(EMErrval+1-RItype)>>1
    if N[Q]==RESET:
        A[Q] = A[Q]<<1
        N[Q] = N[Q]<<1
        Nn[Q] = Nn[Q]<<1
    N[Q]+=1

    # print("run mode after update is A[Q] N[Q] is",A[Q],N[Q])
    return run_interruption_encoding

if __name__ == "__main__":

    # for 8 bits picture
    MAXVAL=255
    RANGE=256
    bpp=8
    qbpp=8
    LIMIT=32
    MAX_C=127
    MIN_C=-128
    RESET = 64
    MAX_C = 127
    MIN_C = -128

    # A，N从0到366，B，C从0到364，Nn从365到366，A初始化为全4，其余初始化都为全0
    A = [4 for _ in range(367)]
    B = [0 for _ in range(365)]
    C = [0 for _ in range(365)]
    N = [1 for _ in range(367)]
    Nn= {365:0,366:0}

    RUNcnt = 0
    RUNindex = 0
    RUNval = 0
    J = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    Pixel_cnt=0

    from PIL import Image

    compress_data_of_each_pictrue=[]

    for i in range(47):
        print("picture",i,"start")
        file_name = 'ARGB_GT/'+str(i)+'.png'
        img = Image.open(file_name)

        # 获取图片大小
        width, height = img.size

        # # 转化为像素矩阵
        
        pixel_matrix_channel_0 = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = img.getpixel((x, y))[0]
                row.append(pixel)
            pixel_matrix_channel_0.append(row)

        pixel_matrix_channel_1 = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = img.getpixel((x, y))[1]
                row.append(pixel)
            pixel_matrix_channel_1.append(row)

        pixel_matrix_channel_2 = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = img.getpixel((x, y))[2]
                row.append(pixel)
            pixel_matrix_channel_2.append(row)

        pixel_matrix_channel_3 = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = img.getpixel((x, y))[3]
                row.append(pixel)
            pixel_matrix_channel_3.append(row)

        pixel_matrix = [pixel_matrix_channel_0,pixel_matrix_channel_1,pixel_matrix_channel_2,pixel_matrix_channel_3]
        # 显示像素矩阵
        # print(pixel_matrix)
        # print(len(pixel_matrix_channel_0))
        # print(len(pixel_matrix_channel_0[0]))


        # pic(index starts from 1)
        # 0     0       90      74
        # 68    50      43      205
        # 64    145     145     145
        # 100   145     145     145

        # origin_pic = [[0,0,90,74],
        # [68,50,43,205],
        # [64,145,145,145],
        # [100,145,145,145]]

        # import random

        # origin_pic = [[random.randint(0, 1) for j in range(8)] for i in range(8)]
        # origin_pic = [[random.randint(0, 0) for j in range(16)] for i in range(16)]

        compress_data_len=0

        for slice in pixel_matrix:
            Pixel_cnt=0
            print("slice[0][0] is",slice[0][0])
            origin_pic = slice
            
            expand_pic = reconstruction_pic(origin_pic)

            outstream = ''
            i,j=0,0
            # while i<len(origin_pic) and j<len(origin_pic[0]):
            import time

            start_time = time.time()

            while Pixel_cnt<len(origin_pic)*len(origin_pic[0]):
                x,a,b,c,d,i,j,EOL = GetNextSample()

                # print()
                # print("**********************************")
                # print(" coding pixel ",i*len(origin_pic)+j)
                # print("**********************************")
                # print()


                D1,D2,D3 = get_gradient(a,b,c,d)
                mode = mode_choose(D1,D2,D3)
                
                
                if mode==1:#regular mode
                    outstream += regular_mode(x,a,b,c,d)
                elif mode==0:#run mode
                    outstream += run_mode(x,a,b,c,d,EOL)

            end_time = time.time()

            # print("     outstream is ",outstream)
            if(outstream == ''):
                print()
                raise Exception("outstream is none!")
            result = outstream
            while len(result)%8 !=0:
                result = result + '0'
            print("now slice is",slice[0][0])
            if(result == ''):
                print()
                raise Exception("result is none!")
            num = int(result,2)
            hexnum = hex(num)[2:]
            # print(hexnum)
            bytenum = len(hexnum)//2
            print("bytenum is",bytenum)
            print("time cost is {:.3f}".format(end_time-start_time))

            compress_data_len+=bytenum
        compress_data_of_each_pictrue.append(compress_data_len)
        print("picture",i,"done,compress is",compress_data_len)
    print(compress_data_of_each_pictrue)