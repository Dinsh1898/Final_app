import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime

# Reading the dataset
data = pd.read_csv("final_processed_file_UPDATED_final_processed_file_UPDATED.csv")
data['Time Stamp'] =  pd.to_datetime(data['Time Stamp'], infer_datetime_format=True)
accuracy_file = pd.read_csv("final_accuracy_file_final_accuracy_file.csv")
accuracy_file['Time Stamp'] =  pd.to_datetime(accuracy_file['Time Stamp'], infer_datetime_format=True)
accuracy_file["month"] = accuracy_file["Time Stamp"].dt.month_name()
#st.write(accuracy_file)
st.set_page_config(layout="wide") 

st.markdown("<h1 style='text-align: center; color: black;'>Exploratory Data Analysis on Forecast</h1>", unsafe_allow_html=True)


min_date = pd.to_datetime((min(data["Time Stamp"])))
max_date =  pd.to_datetime((max(data["Time Stamp"])))
key_list = data.prodHier8.unique()
region_list = data.prodHier2.unique()
state_list = data.State.unique()
quarter_list = data.Quarter.unique()
channel_list = data.prodHier9.unique()
category_list = data.prodHier3.unique()
sub_category_list = data.prodHier4.unique()
abc_xyz_list = data["ABC_XYZ bucket"].unique()


# Side Bar 
st.sidebar.header('Filter for the level at which you want to analyse')
#timestamp = st.sidebar.slider("Time Stamp",min_value=min_date,max_value=max_date)
key = st.sidebar.multiselect("Key",key_list)
region = st.sidebar.multiselect("Region",region_list)
state = st.sidebar.multiselect("State",state_list)
quarter = st.sidebar.multiselect("Quarter",quarter_list)
channel = st.sidebar.multiselect("Channel",channel_list)
category = st.sidebar.multiselect("Category",category_list)
sub_category = st.sidebar.multiselect("Sub Category",sub_category_list)
abc_xyz = st.sidebar.multiselect("ABC XYZ",abc_xyz_list)

# Filtering data based on the selections made by the user
# Key 

data_fil = data
if key:
    data_fil = data_fil[data_fil["prodHier8"].isin(key)]

# Region
if region:
    data_fil = data_fil[data_fil["prodHier2"].isin(region)]

# State 
if state:
    data_fil = data_fil[data_fil["State"].isin(state)]

# Quarter
if quarter:
    data_fil = data_fil[data_fil["Quarter"].isin(quarter)]

# Channel
if channel:
    data_fil = data_fil[data_fil["prodHier9"].isin(channel)]

# category
if category:
    data_fil = data_fil[data_fil["prodHier3"].isin(category)]

# category
if sub_category:
    data_fil = data_fil[data_fil["prodHier4"].isin(sub_category)]

# abc_xyz
if abc_xyz:
    data_fil = data_fil[data_fil["ABC_XYZ bucket"].isin(abc_xyz)]


# Filtering accuracy data based on the selections made by the user
# Key 
data_fil_a = accuracy_file
if key:
    data_fil_a = data_fil_a[data_fil_a["prodHier8"].isin(key)]

# Region
if region:
    data_fil_a = data_fil_a[data_fil_a["prodHier2"].isin(region)]

# State 
if state:
    data_fil_a = data_fil_a[data_fil_a["State"].isin(state)]

# Quarter
if quarter:
    data_fil_a = data_fil_a[data_fil_a["Quarter"].isin(quarter)]

# Channel
if channel:
    data_fil_a = data_fil_a[data_fil_a["prodHier9"].isin(channel)]

# category
if category:
    data_fil_a = data_fil_a[data_fil_a["prodHier3"].isin(category)]

# category
if sub_category:
    data_fil_a = data_fil_a[data_fil_a["prodHier4"].isin(sub_category)]

# abc_xyz
if abc_xyz:
    data_fil_a = data_fil_a[data_fil_a["ABC_XYZ bucket"].isin(abc_xyz)]

# Time series chart 
# Need to resolve why 2022 line is coming till the end
# Adding filters from the multiselect box 
data_grouped = data_fil.groupby(["Time Stamp"])["Target variable"].sum().reset_index()
data_grouped["year"] = pd.DatetimeIndex(data_grouped['Time Stamp']).year

YoY = alt.Chart(data_grouped,title="Historical YoY Trend").mark_line().encode(
    alt.X('monthdate(Time Stamp):O',axis=alt.Axis(title="Timestamp")),
    alt.Y('Target variable:Q',axis = alt.Axis(title = "Actuals (in thousands $)")),
    color='year:Q',
    tooltip = ['Time Stamp','Target variable']
).interactive()
st.altair_chart(YoY,use_container_width=True)

# Historical Future and Actual Values
a = alt.Chart(data_grouped,title = "Actual Value vs Historical  and Future Forecast").mark_line().encode(
    alt.X('Time Stamp:T',axis=alt.Axis(format="%Y %B")),
    alt.Y('Target variable:Q',axis = alt.Axis(title = "Actuals (in thousands $)")),
    tooltip = ['Time Stamp','Target variable']
).interactive()

data_grouped_1 = data_fil.groupby(["Time Stamp","future pred flag"])["Historical Forecast"].sum().reset_index()
data_grouped_1 = data_grouped_1[data_grouped_1["Historical Forecast"] != 0]
#data_grouped["year"] = pd.DatetimeIndex(data_grouped['Time Stamp']).year
b = alt.Chart(data_grouped_1).mark_line().encode(
    alt.X('Time Stamp:T',axis=alt.Axis(format="%Y %B")),
    y='Historical Forecast:Q',
    color = alt.value("#FFAA00"),
    tooltip = ['Time Stamp','Historical Forecast']
).interactive()

data_grouped_2 = data_fil.groupby(["Time Stamp"])["Future Forecast"].sum().reset_index()
data_grouped_2 = data_grouped_2[data_grouped_2["Future Forecast"] != 0]
#data_grouped["year"] = pd.DatetimeIndex(data_grouped['Time Stamp']).year
c = alt.Chart(data_grouped_2).mark_line().encode(
    alt.X('Time Stamp:T',axis=alt.Axis(format="%Y %B")),
    y='Future Forecast:Q',
    color = alt.value("Green"),
    tooltip = ['Time Stamp','Future Forecast']
).interactive()

st.altair_chart(a+b+c,use_container_width=True)

# Bar chart of accuracy and bias
col1, col2 = st.columns(2)
df = data_fil_a.groupby('month').agg({'Abs Error': 'sum','Updated Actual':'sum'}).reset_index()
df['accuracy'] = df.groupby(['month'], group_keys=False).apply(lambda g: 1 - (g["Abs Error"]/g["Updated Actual"]))
df2 = data_fil_a.groupby('month').agg({'Error': 'sum','salesValue':'sum'}).reset_index()
df2['bias'] = df2.groupby(['month'], group_keys=False).apply(lambda g: g["Error"]/g["salesValue"])

bar1 = alt.Chart(df,title = "Accuracy").mark_bar().encode(
    alt.X('month:O'),
    alt.Y('accuracy:Q',axis = alt.Axis(format='%')),
    tooltip = ['accuracy']
).interactive()

bar2 = alt.Chart(df2,title = "Bias").mark_bar().encode(
    alt.X('month:O'),
    alt.Y('bias:Q', axis=alt.Axis(format='%')),
    tooltip = ['bias']   
)

col1.altair_chart(bar1,use_container_width=True)
col2.altair_chart(bar2 ,use_container_width=True)
