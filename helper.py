import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import faostat 
from cProfile import label
import streamlit as st

# plt.style.use('seaborn')

#area code of morocco
mar_code=faostat.get_areas('QCL', https_proxy=None)['Morocco']

# years function returns a tuple containing the first year and last year.
def years(code):
    y=faostat.get_years(code)
    y=[int(k) for k in y.keys()]
    return (min(y), max(y))
#data return a dataframe containing the 20 first items corresponding to the "element" variable
#element parameter can take as a value (Area harvested,Yield,Production Quantity,Stocks, Producing Animals/Slaughtered)
st.cache
def data(code, element):
    y=years(code)
    i=faostat.get_items(code)
    e=faostat.get_elements(code)
    df=faostat.get_data_df(code, pars={
        'areas': mar_code,
        'years': range(y[0],y[1]+1),
        'elements': e[element],
        'items': [i[item] for item in i]
    })[['Item','Year','Unit','Value','Element']]
    ll=df.groupby('Item')['Value'].mean().sort_values(ascending=False).index[:20].tolist()
    return df.query('Item in @ll')
st.cache
def clean_data(df):
    df=df.dropna()
    df['Value']=df['Value'].astype('int')
    df['Value']=df.apply(lambda x: x['Value']*0.05 if x['Unit']=='1000 No' else x['Value'],axis=1)
    df['Unit']=df.apply(lambda x: 'tonnes' if x['Unit']=='1000 No' else x['Unit'],axis=1)
    df['Value']=df.apply(lambda x: x['Value']*1000 if x['Unit']=='1000 Head' else x['Value'],axis=1)
    df['Unit']=df.apply(lambda x: 'Head' if x['Unit']=='1000 Head' else x['Unit'],axis=1)   
    return df

st.cache
def summary_data(df,items):
    new_df = df.query("Item in @items").groupby('Item').agg(min=("Value","min"), max=("Value", "max"), median=("Value", "median"), sum=("Value", "sum"), std=('Value', 'std'), unit=('Unit','first' ))
    new_df['median']=new_df['median'].astype('int')
    new_df['std']=new_df['std'].astype('int')
    return new_df
#draws a graph of the min, median, max of differents items
def summary_graph(df, items):
    new_df=summary_data(df,items)
    X = np.arange(len(items))
    fig= plt.figure()
    plt.bar(X, new_df["min"],width = 0.25, color='g')
    plt.bar(X+0.25, new_df["median"],width = 0.25, color='black')
    plt.bar(X+0.5, new_df["max"],width = 0.25,color='r')
    plt.legend(['min', 'median', 'max'])
    plt.ylabel("Value")
    plt.title("min, median, max of "+ ', '.join(items[:3] if len(items)>3 else items))
    plt.xticks([i + 0.25 for i in range(len(items))], items)

    
def evol(df,items):
    items=sorted(items,key=lambda item: int(df[df['Item']==item]['Year'].tolist()[0]))
    for item in items:
        plt.title(str(df[df["Item"]==item]["Element"].mode()[0]) +' in ' + str(df[df["Item"]==item]["Unit"].mode()[0]))
        plt.xticks(rotation=70)
        plt.xlabel('Years')
        plt.ylabel('Value in ' + str(df[df["Item"]==item]["Unit"].mode()[0]))
        plt.plot(df[df['Item']==item]['Year'], df[df['Item']==item]['Value'], label=item)
    plt.legend()
    plt.show()

def lat_cordinates(s):
    s=s.split('″')
    s=s[0].split('′')+s[1:]
    s=s[0].split('°')+s[1:]
    if len(s)==3:
        return (2*(s[-1]=='N')-1)*(int(s[0])+int(s[1])/60)
    if len(s)==4:
        return (2*(s[-1]=='N')-1)*(int(s[0])+int(s[1])/60+float(s[2])/3600)
def long_cordinates(s):
    s=s.split('″')
    s=s[0].split('′')+s[1:]
    s=s[0].split('°')+s[1:]
    if len(s)==3:
        return (2*(s[-1]=='O')-1)*(int(s[0])+int(s[1])/60)
    if len(s)==4:
        return(2*(s[-1]=='O')-1)*(int(s[0])+int(s[1])/60+float(s[2])/3600)


st.cache
def pop_data(code):
    y=years(code)
    i=faostat.get_items(code)
    e=faostat.get_elements(code)
    df=faostat.get_data_df(code, pars={
        'areas': mar_code,
        'years': range(y[0],y[1]+1),
        'elements': [e[element] for element in e],
        'items': [i[item] for item in i]
    })[['Year','Value','Element']]
    df['Value']=df.apply(lambda x: x['Value']*1000,axis=1)
    df['Value']=df['Value'].astype('int')
    element_map={'Total Population - Both sexes':'Both sexes',
                'Total Population - Male':'Male',
                'Total Population - Female':'Female',
                'Rural population': 'Rural',
                'Urban population':'Urban'
    }
    df['Element']=df['Element'].map(element_map)
    df['Year']=df['Year'].astype('int')

    return df


