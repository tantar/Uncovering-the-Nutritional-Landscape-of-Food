import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly_express as px

pd.set_option('display.max_columns', 5)


st.title("Understanding the Landscape of Nutrition")
st.sidebar.title("Options")
type = st.sidebar.selectbox("Type", ["Individual Food","Comparison","Diet"])
sex = st.radio("What is your Biological Sex?",["Male","Female"])

d = pd.read_csv("data/nutrient_foodname_DRI.csv")



if sex == "Male":
    d.loc[:,"Percent_of_daily_intake"] = ((d.nutrient_value * d.DRI_conv) / d.DRI_MALE).round(3)
else:
    d.loc[:, "Percent_of_daily_intake"] = ((d.nutrient_value * d.DRI_conv) / d.DRI_FEM).round(3)

d = d.drop_duplicates(subset = ["DRI_name","food"])

dl = (d.pivot_table(index = ["food"], columns = ["DRI_name"], values = "Percent_of_daily_intake")
      .reset_index())
colors = px.colors.qualitative.Pastel1
#st.write(dl)

if type == "Individual Food":
    food = st.selectbox("Food", dl.food)

    cfp = dl.loc[dl.food == food,["Carbohydrate","Protein","Total Fiber"]]
    cfp.loc[1,:] = [(1-i) for i in cfp.iloc[0,:]]
    vit = d.loc[(d.food == food) & (d.DRI_name.str.contains("vita",case=False))].sort_values("nutrient")
    min = d.loc[(d.food == food) & (d.DRI_name.str.contains(","))].sort_values("nutrient")
    oth = d.loc[(d.food == food) & ~(d.DRI_name.str.contains(",|vita|prot|carb|fib",case=False))].sort_values("nutrient")
    # Create subplots, using 'domain' type for pie charts
    specs = [[{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}],
             [{'colspan':3},None,None],
             [{'colspan': 3}, None, None],
             [{'colspan':3},None,None]]
    fig = make_subplots(rows=4, cols=3, specs=specs, vertical_spacing= 0.1,
                        subplot_titles= ["Carbohydrates","Proteins","Fiber","Vitamins","Minerals","Other"])

    # Define pie charts
    fig.add_trace(go.Pie(name = "Carbs", labels = ["Met", "Missing"],marker = {"colors":[colors[1],colors[-1]]}, values=cfp.Carbohydrate), 1, 1)
    fig.add_trace(go.Pie(name = "Protein", labels = ["Met", "Missing"], values=cfp.Protein), 1, 2)
    fig.add_trace(go.Pie(name = "Fat", labels = ["Met", "Missing"], values=cfp.loc[:,"Total Fiber"]), 1, 3)
    fig.add_trace(go.Bar(x=vit.DRI_name, y=vit.Percent_of_daily_intake, marker={'color': colors[2]}),2,1)
    fig.add_trace(go.Bar(x=min.DRI_name, y=min.Percent_of_daily_intake, marker={'color': colors[3]}),3,1)
    fig.add_trace(go.Bar(x=oth.DRI_name, y=oth.Percent_of_daily_intake, marker={'color': colors[4]}),4, 1)

    # Tune layout and hover info
    fig.update_traces(hoverinfo='label+text+value', selector=dict(type='pie'))
    fig.update_traces(showlegend=False, selector=dict(type='bar'))
    fig.update_layout( height = 1000)
    fig.update(layout_title_text='Essential Nutrients (per 100 g serving)',layout_title_font_size = 24)

    st.plotly_chart(fig)




elif type == "Comparison":
    st.write("Under Construction")

elif type == "Diet":
    st.write("Under Construction")
    foods = st.multiselect("Foods", dl.food, ["Nuts, almonds", "Blueberries, raw", "Kale, raw"])

    cfp = dl.loc[dl.food.isin(foods),["Carbohydrate","Protein","Total Fiber"]].sum(axis=0).copy()
    vit = d.loc[(d.food.isin(foods)) & (d.DRI_name.str.contains("vita",case=False))].sort_values("nutrient")
    min = d.loc[(d.food.isin(foods)) & (d.DRI_name.str.contains(","))].sort_values("nutrient")
    oth = d.loc[(d.food.isin(foods)) & ~(d.DRI_name.str.contains(",|vita|prot|carb|fib",case=False))].sort_values("nutrient")
    # Create subplots, using 'domain' type for pie charts
    specs = [[{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}],
             [{'colspan':3},None,None],
             [{'colspan': 3}, None, None],
             [{'colspan':3},None,None]]
    fig = make_subplots(rows=4, cols=3, specs=specs, vertical_spacing= 0.1,
                        subplot_titles= ["Carbohydrates","Proteins","Fiber","Vitamins","Minerals","Other"])


    # Define pie charts
    fig.add_trace(go.Pie(name = "Carbs", labels = ["Met", "Missing"], marker = {"colors":[colors[1],colors[-1]]}, sort = False, showlegend = False, values=[cfp.Carbohydrate, (1-cfp.Carbohydrate)]), 1, 1)
    fig.add_trace(go.Pie(name = "Protein", labels = ["Met", "Missing"], sort = False, showlegend = False,  values=[cfp.Protein, (1-cfp.Protein)]), 1, 2)
    fig.add_trace(go.Pie(name = "Fiber", labels = ["Met", "Missing"], sort = False, showlegend = False, values=[cfp.loc["Total Fiber"], (1-cfp.loc["Total Fiber"])]), 1, 3)

    i = 0
    for f in foods:
        fig.add_trace(go.Bar(x=vit.loc[vit.food == f, "DRI_name"], y=vit.loc[vit.food == f, "Percent_of_daily_intake"],
                             hovertext = f, name=f, legendgroup= f, marker={'color': colors[i]}), 2,1)
        fig.add_trace(go.Bar(x=min.loc[min.food == f, "DRI_name"], y=min.loc[min.food == f, "Percent_of_daily_intake"],
                             hovertext = f, name=f, legendgroup= f, showlegend= False, marker={'color': colors[i]}), 3, 1)
        fig.add_trace(go.Bar(x=oth.loc[oth.food == f, "DRI_name"], y=oth.loc[oth.food == f, "Percent_of_daily_intake"],
                             hovertext = f, name=f, legendgroup= f, showlegend= False, marker={'color': colors[i]}), 4, 1)
        i = (i+1)



    # Tune layout and hover info
    fig.update_traces(hoverinfo='label+text+value', selector=dict(type='pie'))
    fig.update_traces(selector=dict(type='bar'))
    fig.update_layout(height = 1000, barmode = "stack")
    fig.update(layout_title_text='Essential Nutrients (per 100 g serving)',layout_title_font_size = 24)

    st.plotly_chart(fig)

