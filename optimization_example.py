'''
Author: guo_win 867718012@qq.com
Date: 2024-01-28 13:31:21
LastEditors: guo_win 867718012@qq.com
LastEditTime: 2024-01-28 14:47:03
FilePath: \optimizationd:\Seafile\私人资料库\sf_2023\#零碳能源系统研究方向\寒假培训\optimization_example.py
Description: 人一生会遇到约2920万人,两个人相爱的概率是0.000049,所以你不爱我,我不怪你.
Copyright (c) 2024 by ${git_name} email: ${git_email}, All Rights Reserved.
'''
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
import json
import os
current_abs_path=os.path.dirname(os.path.abspath(__file__))

def get_load_data() -> dict:
    """get load data from excel

    Returns:
        dict: multienergy load profile
    """
    book_water = pd.read_excel(os.path.join(current_abs_path,'data_source/yulin_water_load.xlsx'))
    # g_demand = list(book_water[''].fillna(0))
    # water_load = list(book_water[''].fillna(0))
    # ele_load = list(book_water[''].fillna(0))
    P_DE = list(book_water['电负荷kW'].fillna(0))
    G_DE = list(book_water['供暖热负荷(kW)'].fillna(0))
    Q_DE = list(book_water['冷负荷(kW)'].fillna(0))
    H_DE = list(book_water['生活热水负荷kW'].fillna(0))
    R_PV = list(book_water['pv'].fillna(0))
    load_json = {
        'P_DE':P_DE,
        'G_DE':G_DE,
        'Q_DE':Q_DE,
        'H_DE':H_DE,
        'R_PV':R_PV
    }
    return load_json

def crf(year:int)->float:
    """usee to calculate capital recovery factor

    Args:
        year (int): decvice life

    Returns:
        float: capital recovery factor
    """
    i = 0.04
    a_e = ((1 + i) ** year) * i / ((1 + i) ** year - 1)
    return a_e

# recommend nomenclature
def Optimization(parameter_json:dict,load_json:dict,time_scale:int) -> dict:
    """

    Args:
        parameter_json (dict): system parameters like device efficiency and capatial cost
        load_json (dict): multi energy load profile
        time_scale (int): variable time scales

    Returns:
        dict: optimal device installed capacity and optimal operation results
    """
    # init parameters
    life = 20 # system life
    c_PV = parameter_json['device']['pv']['capital_cost']# 5000
    c_EL = parameter_json['device']['el']['capital_cost']# 2240  
    c_FC = parameter_json['device']['fc']['capital_cost']# 10000
    c_HS = parameter_json['device']['hs']['capital_cost']# 3000
    c_HW = parameter_json['device']['hw']['capital_cost']# 30
    c_CW = parameter_json['device']['hw']['capital_cost']# 30
    c_HP = parameter_json['device']['hp']['capital_cost']# 8000
    c_EB = parameter_json['device']['eb']['capital_cost']# 100

    lambda_ele_in = parameter_json['price']['ele_TOU_price']
    hydrogen_price = parameter_json['price']['hydrogen_price']
    """Write your code here
    """

    # init model and add variables
    model = gp.Model("HIES")
    P_PV = model.addVar(name='P_PV') # photovoltaic
    P_EL = model.addVar(name='P_EL') # electrolyzer
    P_FC = model.addVar(name='P_FC') # fuel cells
    P_HS = model.addVar(name='P_HS') # hydrogen storage
    G_HW = model.addVar(name='G_HW') # hot water storage
    Q_CW = model.addVar(name='G_CW') # cold water storage

    P_HP = model.addVar(name='P_HP') # heat pump
    P_EB = model.addVar(name='P_EB') # electric boiler
    c_IN = model.addVar(name='c_IN') # Investment cost (CAPEX)
    c_OP = model.addVar(name='c_OP') # Operation cost (OPEX)
    
    p_fc = [model.addVar(name='p_fc_{}'.format(i)) for i in range(time_scale)]#燃料电池
    """Write your code here
    """

    # add constraints
    model.addConstr(c_IN == c_PV * P_PV + c_EL * P_EL + c_FC * P_FC 
                    + c_HS * P_HS + c_HW * G_HW + c_CW * Q_CW + c_HP * P_HP + c_EB * P_EB)
    """Write your code here
    """

    # add objective function and optimize
    model.params.MIPGap = 0.01
    model.setObjective(crf(life) * (c_IN) + c_OP, GRB.MINIMIZE)
    model.optimize()
    """Write your code here
    """
    # Output csv example
    dict_planning = {
        'obj':model.objVal,
        'P_PV':P_PV.x,
        'P_EL':P_EL.x,
        'P_FC':P_FC.x,
        'P_HS':P_HS.x,
        'G_HW':G_HW.x,
        'Q_CW':Q_CW.x,
        'P_HP':P_HP.x,
        'P_EB':P_EB.x,
        'c_IN':c_IN.x,
        'c_OP':c_OP.x,
        'other_plan_results':1,
    }
    dict_operation = {
        'p_fc':[p_fc[i].x for i in range(time_scale)],#燃料电池
        'other_operation_results':1,
    }
    pd.DataFrame(dict_planning,index=['planning']).to_csv(os.path.join(current_abs_path,'Output/dict_planning.csv'))
    pd.DataFrame(dict_operation).to_csv(os.path.join(current_abs_path,'Output/dict_operation.csv'))
    return dict_planning,dict_operation

if __name__ == "__main__":
    with open(os.path.join(current_abs_path,"config.json"), "rb") as f:
        parameter_json = json.load(f)
    load_json = get_load_data()
    time_scale = 8760
    Optimization(parameter_json,load_json,time_scale)