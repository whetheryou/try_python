#coding:utf-8
'''
Created on 2017年7月8日
@author: 吾乃了空大师
1、先标0再标1再标2.。。依次下去，直到没有inf
2、先标出所有0，对于任意一个点，搜索离其最近0点的位置，d=|x1-x2|+|y1-y2|
'''
class Solution:
    def updateMatrix(self, mx1):
        lenx,leny = len(mx1),len(mx1[0]) #长和宽
        #mx2 = [[0 for y in range(leny)] for x in range(lenx)]  #建立lenx行leny列二维列表
        shu = 0 ;zshu = lenx*leny
        mx2 = [[float('inf') if xx==1 else xx for xx in x]for x in mx1]
        for distance in range(max(lenx,leny)):
            for i in range(lenx):
                for j in range(leny):
                    if mx2[i][j] == distance:
                        shu += 1
                        if i+1 in range(lenx): #right
                            mx2[i+1][j] = min(distance+1,mx2[i+1][j])
                        if i-1 in range(lenx): #left
                            mx2[i-1][j] = min(distance+1,mx2[i-1][j])
                        if j+1 in range(leny): #up
                            mx2[i][j+1] = min(distance+1,mx2[i][j+1])
                        if j-1 in range(lenx): #down
                            mx2[i][j-1] = min(distance+1,mx2[i][j-1])
            if shu == zshu:
                print('max distance :',distance)
                break
        print('the rows and columns of matrix: {}{}'.format(lenx,leny),'shu:',shu,zshu)
        return mx2

if __name__=='__main__':
    mx1 = [[0,0,0],[0,1,0],[1,1,1],[1,1,1],[0,0,0]]
    st = Solution()
    mx2 = st.updateMatrix(mx1)
    for cell in mx2:
        print(cell)

        