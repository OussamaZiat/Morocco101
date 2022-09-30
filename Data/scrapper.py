import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get
import streamlit as st

def city_clean(c):
    if c[-1]==']':
        return c[:-3]
    return c
st.cache
def scrap(url):
    response=get(url)
    doc=bs(response.text, features='html.parser')
    table_body=doc.find('tbody')
    rows = table_body.find_all('tr')
    city_dict={}
    for i,row in enumerate(rows[1:]):
        cols=row.find_all('td')
        cols=[(x.text.strip(), x.find('a')['href'] if x.find('a')!=None else "") for x in cols]
        city_dict[i]={}
        city_dict[i]['City']=cols[1][0]
        city_dict[i]['Population']=cols[2][0]
        city_dict[i]['Region']=cols[3][0]
        response2=get("https://en.wikipedia.org/"+cols[1][1])
        doc2=bs(response2.text, features='html.parser')
        city_dict[i]['Latitude']=doc2.find('span', {'class':'latitude'}).text
        city_dict[i]['Longitude']=doc2.find('span', {'class':'longitude'}).text

    df=pd.DataFrame(city_dict).T
    df['Population']=df.apply(lambda x: int(x['Population'].replace(',','')),axis=1)
    df['City']=df.apply(lambda x: city_clean(x['City']),axis=1)
    
    return df

df=scrap("https://en.wikipedia.org/wiki/List_of_cities_in_Morocco")

df.to_csv('City_Pop.csv', index=False)

