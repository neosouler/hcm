import math
from copy import deepcopy

def find_the_chain(pay_calculate_step3):
    pay_calculate_step3.sort()
    for i in range(0, len(pay_calculate_step3)):
        pay_calculate_step3[i].append("Y")
        
    reduced_list = []
    for i in range(0, len(pay_calculate_step3)):
            for j in range(0, len(pay_calculate_step3)):
                    if(pay_calculate_step3[i][1] == pay_calculate_step3[j][2]):
                            for k in range(0, len(pay_calculate_step3)):
                                    if(pay_calculate_step3[k][1] == pay_calculate_step3[j][1] and pay_calculate_step3[k][2] == pay_calculate_step3[i][2]):
                                        if(pay_calculate_step3[i][4] == "Y" and pay_calculate_step3[j][4] == "Y" and pay_calculate_step3[k][4] == "Y"):
                                            if(pay_calculate_step3[i][3] > pay_calculate_step3[j][3]):
                                                pay_calculate_step3[i][4] = "N"
                                                pay_calculate_step3[j][4] = "N"
                                                pay_calculate_step3[k][4] = "N"
                                                reduced_list.append([pay_calculate_step3[i][0], pay_calculate_step3[i][1], pay_calculate_step3[i][2], pay_calculate_step3[i][3]-pay_calculate_step3[j][3]])
                                                reduced_list.append([pay_calculate_step3[k][0], pay_calculate_step3[k][1], pay_calculate_step3[k][2], pay_calculate_step3[k][3]+pay_calculate_step3[j][3]])

    pay_calculate_step4 = []
    for i in range(0, len(pay_calculate_step3)):
        if pay_calculate_step3[i][4] == "Y":
            pay_calculate_step4.append([pay_calculate_step3[i][0], pay_calculate_step3[i][1], pay_calculate_step3[i][2], pay_calculate_step3[i][3]])

    result_list = pay_calculate_step4 + reduced_list

    return result_list


def calculate(pay_id, pay_round_list):
    #하나의 pay_id에 대해서 각 회차별 from, to, price 표시 (from 인원만큼 생성. 금액 또한 나누기)
    #pay_id, from, to(결제자), price 
    pay_calculate_init = []
    for i in range(0, len(pay_round_list)):
            for j in range(0, len(pay_round_list[i].pay_round_member.split(","))):
                    pay_calculate_init.append([pay_round_list[i].pay_id
                    , int(pay_round_list[i].pay_round_member.split(",")[j].replace("'", ""))
                    , pay_round_list[i].pay_round_mst
                    , math.ceil(pay_round_list[i].round_price / len(pay_round_list[i].pay_round_member.split(",")))])


    ##### step1. from==to, 즉 내 돈 주고 내가 먹은 건 제외
    pay_calculate_step1 = []
    for i in range(0, len(pay_calculate_init)):
            if(pay_calculate_init[i][1] != pay_calculate_init[i][2]):
                    pay_calculate_step1.append(pay_calculate_init[i])



    ###### step2. from->to 세트가 같은 내역들 병합
    #합칠 자리를 먼저 만들어 놓는다. 중복값을 찾고 제거하기 위해 price를 일단 0으로 만들고
    temp_list = deepcopy(pay_calculate_step1)
    for i in range(0, len(temp_list)):
            temp_list[i][3] = 0
    #중복값 제거, 합칠 자리 완성
    add_target = []
    for x in temp_list:
            if x not in add_target:
                    add_target.append(x)

    pay_calculate_step2 = deepcopy(add_target)
    for i in range(0, len(pay_calculate_step1)):
            add_price = pay_calculate_step1[i][3]
            if(temp_list[i] in add_target):
                    #add_target에서 넣어야 할 idx를 찾고
                    idx = add_target.index(temp_list[i])
                    
                    #이제 잘 찾아서 더하기면 하면 됨    
                    pay_calculate_step2[idx][3] = pay_calculate_step2[idx][3] + add_price



    ##### step3. 상호간의 거래 상쇄
    pay_calculate_step3 = []
    index_list_step3 = []
    for i in range(0, len(pay_calculate_step2)):
            for j in range(i+1, len(pay_calculate_step2)):
                    if(pay_calculate_step2[i][1] == pay_calculate_step2[j][2]):
                            if(pay_calculate_step2[i][2] == pay_calculate_step2[j][1]):
                                    #상쇄 건의 index를 남기고 pay_calculate_step3에 차액을 미리 넣어둔다
                                    index_list_step3.append(i)
                                    index_list_step3.append(j)
                                    
                                    if pay_calculate_step2[i][3] > pay_calculate_step2[j][3]:
                                            pay_calculate_step3.append([pay_calculate_step2[i][0], pay_calculate_step2[i][1], pay_calculate_step2[i][2], pay_calculate_step2[i][3]-pay_calculate_step2[j][3]])
                                    else:
                                            pay_calculate_step3.append([pay_calculate_step2[j][0], pay_calculate_step2[j][1], pay_calculate_step2[j][2], pay_calculate_step2[j][3]-pay_calculate_step2[i][3]])

    for i in range(0, len(pay_calculate_step2)):
            if i not in index_list_step3:
                    pay_calculate_step3.append(pay_calculate_step2[i]) 




    ##### step4. 트랜잭션을 최소화 할 수 있는 놈을 찾자
    ##### 꼬리에 꼬리를 물 수 있을 때, 그 시작점(j)이 되는 놈이 앞쪽(i)에 더해지고, 뒷쪽(k)에서는 빼진다
    templist1 = find_the_chain(pay_calculate_step3)
    templist2 = find_the_chain(templist1)
    templist3 = find_the_chain(templist2)
    templist4 = find_the_chain(templist3)
    templist5 = find_the_chain(templist4)
 
    pay_calculate_step4 = templist5
    pay_calculate_step4.sort()
    
    #보내야 할 금액이 0원이면 아예 리스트 pop 그리고 완성
    index_list_step4 = []
    for i in range(0, len(pay_calculate_step4)):
            if(pay_calculate_step4[i][3] == 0):
                    index_list_step4.append(i)

    if index_list_step4: 
        for index in index_list_step4:
                pay_calculate_step4.pop(index)


    return pay_calculate_step4