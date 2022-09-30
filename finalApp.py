import pandas as pd 
import faostat 
import streamlit as st 
from helper import *
import plotly.express as px


st.set_page_config(layout='wide')



c1, c2, c3 = st.columns(3)


c3.image('../mar_flag.png', width=400)
c1.markdown('<h1 style="text-align:center;color:#694C4C;font-weight:bolder;font-size:70px;">MOROCCO 101</h1>',unsafe_allow_html=True)
# st.markdown('<h2 style="text-align:center;color:;">An analysis..</h2>',unsafe_allow_html=True)
st.markdown("#### This is an analysis based project on the population and crops production in Morocco")

# @st.cache
#_____________________________________________________________________________________
mar_code=faostat.get_areas('QCL', https_proxy=None)['Morocco']





#_____________________________________________________________________________________
domain=st.sidebar.selectbox('Domain', ['Production',"Annual Population","Population map"], 0)

domain_dict={'Production':'QCL',"Annual Population":"OA","Population map": 'PM'}
code=domain_dict[domain]
#__________________________________________________________________________________________________________________________________________
if code=='QCL':
  st.markdown(f'<h2 style="text-align:center;color:#694C4C;">Crops and livestock products</h2>',unsafe_allow_html=True)

  elements= faostat.get_elements(code)
  element = st.sidebar.selectbox('Elements', elements, 2)
  df=data(code,element).reset_index(drop=True)
  df=clean_data(df)

  df["Year"]=df['Year'].astype('int')
  yrs = st.sidebar.slider("Years", int(df.Year.min()), 2025, (1970, 2000))
  df=df.query(f"Year.between{yrs}").fillna(0).sort_values(by=['Year',"Item"])

  items=st.sidebar.multiselect("items",df['Item'].unique().tolist())
  st.write(f'The following table contains production data( {element} ) for primary products from {yrs[0]} to {yrs[1]}: ')
  st.dataframe(df.drop("Element", axis=1), use_container_width=True)
  if len(items)==0:
      st.markdown(f'<h4 style="text-align:left;color:#694C4C;">You can add some items in the sidebar to obtain additional data... </h4>',unsafe_allow_html=True)

  if len(items)>0:
    sum_df=summary_data(df,items).reset_index()
    
    st.dataframe(sum_df, use_container_width=True )
    if len(items)>1:
      fig=px.pie(sum_df, values=sum_df['median'],hole=0.48, names=items, title=f'{element} of {", ".join(items)} between {yrs[0]} and {yrs[1]} ',width=1000, height=500,color_discrete_sequence=px.colors.sequential.RdBu)
      fig.update_layout(
        margin=dict(l=20, r=20, t=70, b=20),
        # paper_bgcolor="LightSteelBlue",
    )

      st.plotly_chart(fig, use_container_width=True)

    fig2 = px.line(df.query('Item in @items')
                  , x='Year'
                  , y='Value'
                  , color='Item' 
                  , title = f'{element} of {", ".join(items)} between {yrs[0]} and {yrs[1]} '
                  , width=1000
                  , height=500
                  , hover_data=["Year", "Value", "Unit"],
                  color_discrete_sequence=px.colors.sequential.RdBu
                    )

    st.plotly_chart(fig2, use_container_width=True)
#_________________________________________________________________________________________________________________________________________


#__________________________________________________________________________________________________________________________________________
if code=='OA':
  st.markdown(f'<h2 style="text-align:center;color:#694C4C;">Annual population</h2>',unsafe_allow_html=True)

  df=pop_data(code)
  elements= ['Both sexes', 'Male vs Female', 'Urban vs Rural']
  element = st.sidebar.selectbox('Elements', elements, 0)
  yrs = st.sidebar.slider("Years", int(df.Year.min()), 2025, (1970, 2000))
  #################################################################################
  if element=='Both sexes':
    dff=df.query('Element == "Both sexes"').query(f"Year.between{yrs}")
    st.dataframe(dff,use_container_width=True)
    fig = px.line(df.query('Element == "Both sexes"').query(f"Year.between{yrs}")
                  , x='Year'
                  , y='Value'
                  , title = f'Annual popualtion between {yrs[0]} and {yrs[1]} '
                  , width=1000
                  , height=500
                  , hover_data=["Year", "Value"],
                  color_discrete_sequence=px.colors.sequential.RdBu
                    )
    st.plotly_chart(fig, use_container_width=True)
  #################################################################################
  elif element=='Male vs Female':
    sex=['Male', 'Female']
    dff=df.query('Element in @sex').query(f"Year.between{yrs}")
    st.dataframe(dff,use_container_width=True)
    fig = px.line(dff
                  , x='Year'
                  , y='Value'
                  , color='Element'
                  , title = f'Annual popualtion of males and females between {yrs[0]} and {yrs[1]} '
                  , width=1000
                  , height=700
                  , hover_data=["Year", "Value"],
                  color_discrete_sequence=px.colors.sequential.RdBu
                    )
    st.plotly_chart(fig, use_container_width=True)

    pie_data=dff.groupby('Element').agg(median=('Value',"median")).reset_index()
    pie_data['median']=pie_data['median'].astype('int')
    fig2=px.pie(pie_data, values=pie_data['median'],hole=0.48, names=pie_data['Element'], title=f'Annual popualtion of males and females between {yrs[0]} and {yrs[1]} ',width=1000, height=500,color_discrete_sequence=px.colors.sequential.RdBu)
    fig2.update_layout(
      margin=dict(l=20, r=20, t=70, b=20),
      # paper_bgcolor="LightSteelBlue",
  )
    st.plotly_chart(fig2, use_container_width=True)
  
    year=st.slider('Choose a year: ', min_value=yrs[0], max_value=yrs[1], step=1, value=int((yrs[0]+yrs[1])/2))
    pie_data2=df.query('Year==@year').query('Element in @sex').sort_values(by='Element')
    fig3=px.pie(pie_data2, values=pie_data2['Value'], names=pie_data['Element'], title=f'Annual popualtion of males and females in {year} ',width=1000, height=500,color_discrete_sequence=px.colors.sequential.RdBu)
    fig3.update_layout(
      margin=dict(l=20, r=20, t=70, b=20),
      # paper_bgcolor="LightSteelBlue",
  )
    st.plotly_chart(fig3, use_container_width=True)


  ##################################################################################
  elif element=='Urban vs Rural':
    L=['Urban','Rural']
    dff=df.query('Element in @L').query(f"Year.between{yrs}")
    st.dataframe(dff,use_container_width=True)
    fig = px.line(dff
                  , x='Year'
                  , y='Value'
                  , color='Element'
                  , title = f'Annual popualtion between {yrs[0]} and {yrs[1]} '
                  , width=1000
                  , height=700
                  , hover_data=["Year", "Value"],
                  color_discrete_sequence=px.colors.sequential.RdBu
                    )
    st.plotly_chart(fig, use_container_width=True)
    pie_data=dff.groupby('Element').agg(median=('Value',"median")).reset_index()
    pie_data['median']=pie_data['median'].astype('int')
    fig2=px.pie(pie_data, values=pie_data['median'],hole=0.48, names=pie_data['Element'], title=f'Annual popualtion between {yrs[0]} and {yrs[1]}',width=1000, height=500,color_discrete_sequence=px.colors.sequential.RdBu)
    fig2.update_layout(
      margin=dict(l=20, r=20, t=70, b=20),
      # paper_bgcolor="LightSteelBlue",
  )

    st.plotly_chart(fig2, use_container_width=True)
    year=st.slider('Choose a year: ', min_value=yrs[0], max_value=yrs[1], step=1, value=int((yrs[0]+yrs[1])/2))
    pie_data2=df.query('Year==@year').query('Element in @L').sort_values(by='Element')
    fig3=px.pie(pie_data2, values=pie_data2['Value'], names=pie_data['Element'], title=f'Annual popualtion in {year}',width=1000, height=500,color_discrete_sequence=px.colors.sequential.RdBu)
    fig3.update_layout(
      margin=dict(l=20, r=20, t=70, b=20),
      # paper_bgcolor="LightSteelBlue",
  )
    st.plotly_chart(fig3, use_container_width=True)
#__________________________________________________________________________________________________________________________________________
if code=="PM":
  
  df=pd.read_csv('./Data/City_Pop.csv')
  df['Latitude']= df.apply(lambda x: lat_cordinates(x['Latitude']),axis=1)
  df['Longitude']= df.apply(lambda x: long_cordinates(x['Longitude']),axis=1)
  st.dataframe(df,use_container_width=True)

  pie_data3=df.groupby('Region').agg(Population=('Population','sum')).reset_index()
  fig3=px.pie(pie_data3, values=pie_data3['Population'], names=pie_data3['Region'], title='',width=1000, height=500,color_discrete_sequence=px.colors.sequential.RdBu)
  fig3.update_layout(
    margin=dict(l=20, r=20, t=70, b=20),
    # paper_bgcolor="LightSteelBlue",
  )
  st.plotly_chart(fig3, use_container_width=True)

  st.subheader('Population density map of Morocco:')
  fig = ( px.density_mapbox( data_frame=df, lat=df['Latitude'],lon=df['Longitude'], 
center=dict( lat=33, lon=-3 ), height=700,
 z=df['Population'], color_continuous_scale=px.colors.sequential.Agsunset,hover_name='City', hover_data=['Population', 'Region'] , zoom=5, radius=25, mapbox_style="carto-positron", ) )  

  st.plotly_chart(fig, use_container_width=True)









