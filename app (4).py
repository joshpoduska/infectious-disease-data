import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import json
import pandas as pd
import numpy as np
import plotly
from plotly.tools import mpl_to_plotly
from datetime import datetime
import subprocess

##############################################################
#code to pull data
#repeated in the app_callback function below for refreshing
completed = subprocess.run(['sudo', 'rm', '-r', 'COVID-19/'], \
                            stdout=subprocess.PIPE,)
print(completed.stdout.decode('utf-8'))

completed = subprocess.run(['git', 'clone', 'https://github.com/CSSEGISandData/COVID-19.git', 'COVID-19'], \
                        stdout=subprocess.PIPE,)
print(completed.stdout.decode('utf-8'))

mypath = 'COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/'

from os import listdir
from os.path import isfile, join
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f != 'README.md' and f != '.gitignore']
onlyfiles.sort()
print(onlyfiles[0], onlyfiles[-1])
global firstdate
global lastdate
firstdate = onlyfiles[0][:-4]
lastdate = onlyfiles[-1][:-4]

i = 0
for f in onlyfiles:
    # data format changed on 3-23
    if datetime.strptime(f[:-4] , '%m-%d-%Y') < datetime.strptime('03-22-2020', '%m-%d-%Y'):
        df = pd.read_csv(mypath + f)
        df = df[['Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered']]
        df = df.groupby(['Country/Region']).sum()
        df['Date'] = f[:-4]
        if i == 0:
            dfs = df
        if i > 0:
            dfs = pd.concat([dfs, df])
        i += 1
    else:
        df = pd.read_csv(mypath + f)
        df = df[['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']]
        df.columns = ['Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered']
        df = df.groupby(['Country/Region']).sum()
        df['Date'] = f[:-4]
        if i == 0:
            dfs = df
        if i > 0:
            dfs = pd.concat([dfs, df])
        i += 1

names = dfs.index.tolist()
names = [x.strip() for x in names]
changelist = [i for i, value in enumerate(names) if value == 'Mainland China']
for c in changelist: names[c] = 'China'
changelist = [i for i, value in enumerate(names) if value == 'Republic of Korea']
for c in changelist: names[c] = 'South Korea'
changelist = [i for i, value in enumerate(names) if value == 'Korea, South']
for c in changelist: names[c] = 'South Korea'
changelist = [i for i, value in enumerate(names) if value == 'Iran (Islamic Republic of)']
for c in changelist: names[c] = 'Iran'
changelist = [i for i, value in enumerate(names) if value == 'Iran (Islamic Republic of)']
for c in changelist: names[c] = 'Iran'
changelist = [i for i, value in enumerate(names) if value == 'occupied Palestinian territory']
for c in changelist: names[c] = 'Israel'
changelist = [i for i, value in enumerate(names) if value == 'United Kingdom']
for c in changelist: names[c] = 'UK'
changelist = [i for i, value in enumerate(names) if value == 'Hong Kong SAR']
for c in changelist: names[c] = 'Hong Kong'
changelist = [i for i, value in enumerate(names) if value == 'Taipei and environs']
for c in changelist: names[c] = 'Taiwan'
changelist = [i for i, value in enumerate(names) if value == 'Taiwan*']
for c in changelist: names[c] = 'Taiwan'
changelist = [i for i, value in enumerate(names) if value == 'Republic of Ireland']
for c in changelist: names[c] = 'Ireland'
changelist = [i for i, value in enumerate(names) if value == 'Czechia']
for c in changelist: names[c] = 'Czech Republic'
changelist = [i for i, value in enumerate(names) if value == 'Macau']
for c in changelist: names[c] = 'Macao'
changelist = [i for i, value in enumerate(names) if value == 'Macao SAR']
for c in changelist: names[c] = 'Macao'
changelist = [i for i, value in enumerate(names) if value == 'Republic of Moldova']
for c in changelist: names[c] = 'Moldova'
changelist = [i for i, value in enumerate(names) if value == 'Cote d\'Ivoire']
for c in changelist: names[c] = 'Ivory Coast'
changelist = [i for i, value in enumerate(names) if value == 'Viet Nam']
for c in changelist: names[c] = 'Vietnam'
changelist = [i for i, value in enumerate(names) if value == 'Russian Federation']
for c in changelist: names[c] = 'Russia'
changelist = [i for i, value in enumerate(names) if value == 'Congo (Kinshasa)']
for c in changelist: names[c] = 'Congo'
changelist = [i for i, value in enumerate(names) if value == 'DR Congo']
for c in changelist: names[c] = 'Congo'
changelist = [i for i, value in enumerate(names) if value == 'North Ireland']
for c in changelist: names[c] = 'Ireland'
changelist = [i for i, value in enumerate(names) if value == 'St. Martin']
for c in changelist: names[c] = 'Saint Martin'
dfs.index = names
dfs.index.rename('Country', inplace=True)
dfs['Date'] = pd.to_datetime(dfs['Date'])

#get population data
dfp = pd.read_csv('populations.csv')
dfp.index = dfp.Country.values
dfp.drop(['Country'], axis=1, inplace=True)
dfp.index.rename('Country', inplace=True)

#join with covid data
dfsj = dfs.join(dfp, how='outer')
dfsj['Population'] = pd.to_numeric(dfsj['Population'])
dfsj.dropna(inplace=True)
dfsj['Per1MConfCases'] = 1000000* dfsj.Confirmed/dfsj.Population
dfsj['Per1MDeaths'] = 1000000* dfsj.Deaths/dfsj.Population

#country as a col
dfsj.reset_index(level=0, inplace=True)
dfsj = dfsj.sort_values(['Country', 'Date'])

#globals
global dfd1
global dfc1
global dfmain
global dfmain10

#aligned by 1st death or case
dfd1 = dfsj[dfsj['Deaths']>=20]
dfc1 = dfsj[dfsj['Confirmed']>=600]

#main table on latest date
dfmain = dfsj.loc[dfsj.groupby(["Country"])["Date"].idxmax()]
dfmain = dfmain.sort_values('Deaths', ascending=False)
dfmain10 = dfmain.sort_values('Deaths', ascending=False).head(10)
# dfmain10 = dfsj.loc[dfsj.groupby(["Country"])["Date"].idxmax()].head(10)
# print(dfmain10)

lastupdated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

################################################################
#begin app code

app = dash.Dash()

app.scripts.config.serve_locally = True
# app.css.config.serve_locally = True

################################################################
# Configure path for dependencies. This is required for Domino.
#Learn more about Dash on Domino https://blog.dominodatalab.com/building-domino-web-app-dash/

# For Dash >= 0.18.3
app.config.update({
#### as the proxy server may remove the prefix
'routes_pathname_prefix': '',

#### the front-end will prefix this string to the requests
#### that are made to the proxy server
'requests_pathname_prefix': ''
})

# For Dash < 0.18.3
# app.config.routes_pathname_prefix=''
# app.config.requests_pathname_prefix=''


plotlycolors = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
]



#################################################################


# see here for details on updating pages with refresh. https://dash.plot.ly/live-updates

def serve_layout():
    return html.Div([
    html.Div(
        html.A([
            html.Img(src=('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZMAAAB9CAMAAABQ+34VAAAAllBMVEX///9aX2pRiMdXXGdJT1xQVWFUWWVNU19VWmZpbXdKUF14fITS09VPVGGwsrbi4+TJys3AwsWkpqtjaHKZnKJ+gomqrbF0d4Da2txucnv09PXc3d/s7O1dYm2KjZTo6eo8fcOOkZi4ur7t8vi3y+WeoKZcjsqhu956odLU4O+Eh49CSFbg6PRql81zndCjvd6LrNfJ1+tuoUP2AAANn0lEQVR4nO1d2WKjOBaFgBDGxnhf8BbT5Vrs6p6Z//+5QUKS0QYYBElXdN6CgUgcdPcrHOdVTEfedvbyVRY9Yhy7rudvKs74/ddgg7FAmEMX4XHUnfDj/f39b8vKkACYEjfO1D9/e3/DSIcd1ZfGLSg4AUpOfn0nlLz9GHpgXxdHv6DE9Q/yj3/9pIy8vf0z/Ni+KsZeQYk3ln/78WTk7e3n8GP7ophEdJlIKv5bmZG3928fMbwviRNZJsFN+OGpSApK/v6Q4X1FZMTocgF/vKxIMCX/+ZjxfUGk0FUawj8ERn5a72QwrIgd7C3LR7+98Yz8/fujxvcFkTA7ePc8KCiStzer3HvDbJOJrviWKPjwzg5JisS6ir0hPcEA+Hzwd8bsYEaWVSQDYomXxONSPuZSm2tBDoiK5PuvDxjpl8Eukr2QDbWDQ3Lgp1UkQ2JePP9w/TyUUgUPiUQT/HarSHqGgpNzSOzgPTnwj1Ukg0Lm5MDs4IQc+a5RJEk2rcBk0Hn8SZA5GdFA15Ue+a9akZx9UIVoaZNd7SBxMqdRlYg90t/vKkWyoCfqEI4GnMefBImTgNrB0+dJv97e3yVFEunZoKzuHIsWEDlZEDvYc7nTfv1PVO0sDakHmA8yhT8OAifsSUe1KrqeE7tO2kHg5E7s4FCR8BWwimso8U49j/1PBc8Jcxf9S811ObZRUAXoaevCLCrBc3IhijtYNbl2srhVwCqTthBkF1kn8ccO6otD4GSF//Q1lY8Wg0C0hde5c/4QS1UsBoXkMx6mWQP9btEjFHFhiw+GWU4mExt37A6TnGQ+hL7VRZ1hkJM5NqQDdWuERXMY5IRWGMdLG+fqBIOcsKCk599tWKUDDHJSSqiE/qL+fAuK3epaylaZ5OQaPEnJ1YqNdzXFyg9CAJ6ixSAn6QmUSHHhyKqVRphhoV+qljfqn9z8sJw/8e/WW2mAdfHQILNXzfqMx7vvlVixaqUJluSRQXrAdGxlt+TSjyCwaqUONLfLklbm410ZKOv6XK0oWrktStiJyd1Z8VqH1+rrXsKNE2D9qZX0cjgc/j2e0DEf7UX1KKQiiMKr8I1Wkh7XjdVKNtpzWK+yRusqze6eH0EII3+5qhj8Mr/ntuqd2OUnjOQ38pwfXibSycv9SB06mubzqKgrma2WZLTeeS4Oh1VBRKRofvYIvdA3uUwQJkuuShKEuh2nprHHIQwAhNc6WpK7DxjrXgCBdu+kKL9nUCWYA3SC/DTH+XFf4mSS385XTmUDPG3dZ7qAccCGGwL/LGSopKK65Dwa96CIBbWiixdPubPYwtpW5tWunM2NSYeaKeBXw9d7StNYrU3RLhpQ5gSdLW/ikGMTuJ6GkywS5yitAUpYPFXfwhh4tfKQJoiBOQkhAyheqPChF3eHoJhjvqKiKIJkwUD1YsCc6J4W/f01TvheaAI9J1tIlkcxWjJ2j7v3jEoVv2+PjlMrGvGCOAmvyYFgMl9sfTxsqJPOxO2F3m2WHI+XXXaP8NIPlHX8xWShTnQWey+9xkmp4+AJHSepi5c0iM7Z7nI8HuarMEYPxeM1+F5qZugNJbUS6DkJ+DWRLiI0wmCvvGCCKYlH5SlNIZ6mqu6S/n/1+Ih2fZET15cFpYaT1EUjC7mdH2ZLIAnUpGoTKNNgaiVSv6oKTvKZjNGolar5iO1Ef6q8QLG0YKWgvoatOFGUiWo42aJ/AMTbbzADsLyuaQDXU7+JhrHCAgxo/peSk/wi9CyhwuzEHUsKy/0K1BfQdQJVgo2+nS9zIi9JNScb9O9juagUy19vWzqS0kyHzljpiiQr2+CXtR/5Z82pGk6cc6DUeBmapNIaxZG8SLoAIqkJNNW24/ya0y18nRM3EOej5ASLRqWKmEei6JiKzdZmcfdj8CgLizTRmhM6TnAmWZ4OYkpTzBwqf8o5ARMkohQWLFJN8TxX8y9xEmCNFglLUskJEkia7oKikbd8hKbOQR9x2yt+mdSulQQtJ3hPN3GhzNGtgeJshzT9SSsLcTJH76snP/dcDuZe2upFTvxCIgkOpYoTvEw0jTz4N84crNjErjNopMBrdLaWE2weisaa6hgDfslEjYI5cRaBwnFETkH+VF7nBMs8oZFNxQkSR1rXCFnh/LaOYxr2umsuaY8DUav6eEcZek5QxFpwz3AXmdatmkqzdCgnjurpuMWxFpwUIpR7dCpOkD2iTYFfJDlwUW0GZQbP/Vab+KR6TvB649cxpmmrOhmhmKVwkHCCtu0THEd0CM2+DSd4DwFYVpkKTtLKNwjrD8AJNvWmaUbANprS2Vpl6DnBr1nMPUc0aK3oKt5eKLxjhJNCg3K/xMQGbsNJ7qW6vH+n4ASdXPF4FZOhppfKCeiGl3zSCk7kQW8lljggc1iUFZQTtP1Vub28UDGJ05ITZx3wKlPBCVqIFXkptOiF1zZj3pT2qrZgPmmDTQsqOJlKc8LDVccyEW6Ke1FOsHlQchyRYClu3o4TBwVNSp24Ck5u1at6AmVBTFPzzXoXX8ErPmkFJ8jw9ThFim1LvaW4CeTZME6QCij9iN6bQta35ARLg5g9cgUnyCuqKJ5O0FMSnBcpDWwOzCcN6k/VczIDoh1VrTSVwoJxgjOszGRANg7Zs6wlJ04WlU0kBSf3KrOL9vMKB1m9hPn4MNswutYnHY4TZA8y0x+pHiK023Li3JGIBmQ4hjhhzp35UGRzn7RKdgExOthFdhU2AzE7kIygGr81J/jNoxrBjOxiaeA++uaoT6qIaPAYTMc7uByEvH/IzKaxvvacYCePhKfM6HgH1QegWUY9RIefPmlNQczLtjBoZwvj/xUTxxFHVejR9pwU0d1ihl1s4Uv5/+z8wPMi8+EVp7lPOpTPiOERCZ7bsc9xdeCksPqxhd3eZ9y5fhSVJnVc7dc95VAa+qQDxVbI9RBL+Cwuh2u7cIIdihDJw9axleSBU37eEJ/3a+iT1sQgeR3YPgZJUOgRl2O2Eyc4FQ1WHWKQ1PqNtnpFaQzNfNJhYvUUO+w4BlzYpxMnRRbXn7WP1Z/Iq+t6/rX31pBmPmlNTkswfHHF+es5reefa7RQ+BRFN06KHWqi9OWcFpoeMjiWLkMQ9V1yx1alXgM4Nblf2WoB+oWnTgsLnBB7sMx1R06whPL2mTL3G9bnfunX/TBit2e18tzHsOIfvVojEbtVNRLyBQInhT3IUdeVE/zGeyeVmMJPQCqnwPPAywQPzOMqV3tRK+mc7fas2e+TQ2UtkWIpt6gl4jiRjaGunJAqQKXqwDv/w5paoqvQGmJcrcweAER0cKp9cQW8XHOHH4D4DeLKmjve9Jk++Jqa7pw4N6DjxNkXNXfCU17wNXeXbVRmxbRaSR5u6eEo9o8WoeDkWF2biv8DWJbkV7qJqmpTBXN0MudXWXdOSLWvujYVkRLCaekBzIr+6EfJu525XMs0OJlUKySdRQtt6kuTixruHcVkvtjX1nBjAuJgNd9dLslkui4u0NZw13TqG+AkBTpOnPSEBwf8dTZJLpfd/AqgoobbmXINEV40NpdAIbl4GpQ61NrDul6HitauQ1gMP4xhFOVXFOZdpO116J+TQqVoXJEx63VAwyWjDVzx3ulV6G1bmVIrhBMWpqJpYO1zUfYEBX71a6LoCYr1PUEDcII379f2BEEgzU9lzidbbrv5QGXitIHICU0D6zkReue8AERgVWcPXs4+YLR4AQy1w488ryYDvQIv9s4p7zKu6J3LnXzIeue8EPhXzRsnqRUjXaYiJ86mqHp+6Bai0GO6bdxjOr+eUN9T5MP9rbrHdFmtMBej/Uh2Ic4jTY/pXrO7eH5BRY/p5DaK/Ah1ap2uVa/I1OfUipE9HyROnBEK+oi2qyEck0TZ3Pw5kV6SpLYUWFArmo7DlyBz4tygf7KbSTRHsi+1TEtfwG4BBScWr2LmMbVion7FcmIEG2pYmthc03JiBukZq5WwvkCuHpYTUzjsfegvTbQHWU7MIZmZCdtbTj4fLCefA5Pps/PacvIZkC4j8Pz+vOXkM2CELWn6/XnLyScASSXSqgPLSVekh50ezQwxstkF7SKznHTE1YcViCoq2BlodRKtxLKcdMNaTH+JeNSmVI5iS4PlpBNYrlyL+t75NYn1s9Yfy0knZHXLRFFWOD+fy6kQuUXOctIJ8wac8FdMTnEYwlLWmbWSssyL5aQT0kcdJfwuL5dxUa33TLOwlutnpbvlpBvmj9CrAgi5slpWv0NXT8q6fp7yzHLSEYfzsgKjcs1EBp/1FFR5qLbwsJwMhVyRlEQa+Wi2cqsby8kwuKy5sm/ao6rcEspyMghWQnsEiWzNqB3M1cwTh0XsiLYwiSzmvzCzp2EwShS/xeA8Kos3ix4gfjLj2cW9Yd4Nf8UYel5YH5SxaAnp0zLPJSF9RoUh25/OA3R6f1GIn2A6lxRHo55eC8MQP1W2L5e7P3vf7ZIYDDtBkQif9BsN97kOCwK9IsFo0DtqYRhbvjHlLD55Fns0vg+uhQa7crZL8c1LmvDVbFth0QOmz8wKCOV2HraHnWZ7F4sewDKQ6o5oFg/uYR9JCw1Itkv3UVi6hnr4ToeFFhn6tqn248lkszQTrXYWzbG7L/XfNiXbDWm2NrP4EKA9XLyHTZF8KtyW3t1+Fd4I/g8rY9mfnkXIIwAAAABJRU5ErkJggg=='), \
                style={'height':'10%', 'width':'10%'})
                    #,'padding-left':'3%'
             ], href='https://www.dominodatalab.com', target="_blank")
            #  , style={'display': 'inline-block'}
            ),
    html.Div('Built on and hosted by ', style={'display': 'inline-block'}),
    html.Div(
        html.A('Domino', href='https://www.dominodatalab.com', target='blank'), 
        style={'display': 'inline-block', 'padding-left': '0.5%'}),
    html.P(html.Br()),            
    html.H2('Coronavirus COVID-19 Global Data'),
    html.H6('Based on the 2019 Novel Coronavirus Data Repository by Johns Hopkins CSSE'),
    html.A("COVID-19 Source Data", href='https://github.com/CSSEGISandData/COVID-19', \
        target="_blank", style={'padding': 10}),
    html.A("Population Source Data", \
        href='https://www.worldometers.info/world-population/population-by-country/', target="_blank"),
    html.P(html.Br()),
    html.H6('This web app offers a unique look at COVID-19. Instead of plotting COVID-19 by calendar date \
    it is plotted by days since a certain number of deaths or confirmed cases. \
    This allows for better country-to-country comparisons.'),
    html.Div(id='refresh-data', style={"display": "none"}),
    html.Div(id="last-update", style={"display": "none"}),
    html.P(html.Br()),
    html.P(['Last data pull on ', lastupdated]),
    html.P('The data source is updated only once a day.'),
    html.P('Refreshing this page pulls any new data from the source location.'),
    html.P(['First date of data set: ', firstdate]),
    html.P(['Last date of data set: ', lastdate]),
    html.P(html.Br()),
    html.H4('Top 10 Countries by # of Deaths', style={'text-align': 'center'}),
    html.H6('Select rows & view interactive graphs below', style={'text-align': 'center'}),
    dt.DataTable(
        rows=dfmain10.to_dict('records'),
      
        # optional - sets the order of columns
        columns=dfmain10.columns,
        row_selectable=True,
        filterable=False,
        sortable=True,
        selected_row_indices=[],
        id='datatable-gapminder'
    ),
    html.Div(id='selected-indexes'),
    html.P(html.Br()),
    html.P(html.Br()),
    html.H6('These graphs turn back the clock and give all countries a common starting point. The day a country reached 20 COVID-19 deaths was \
    selected as the common starting point for deaths. The day a country reached 600 confirmed COVID-19 cases was selected as the common \
    starting point for cases. These were the rounded counts for China on the first day they reported data. That is as far back in time as we can go. \
    All country data is aligned to these starting points for better country-to-country comparisons', style={'text-align': 'center'}),
    html.P(html.Br()),
    html.H5('***YOU HAVE TO SELECT SOME COUNTRIES IN THE TABLE ABOVE BEFORE THE GRAPHS APPEAR BELOW***', style={'text-align': 'center', 'color': 'red'}),
    html.P(html.Br()),
    html.P(html.Br()),
    dcc.Graph(
        id='graph-trends'
    ), 
    html.H4('All Countries', style={'text-align': 'center'}),
    html.H6('Selecting a country highlights it orange in the bar charts below. Filtering rows removes countries from the table and the bar charts. \
    Sorting columns changes the order of the table and the bar charts.', style={'text-align': 'center'}),
    dt.DataTable(
        rows=dfmain.to_dict('records'),
      
        # optional - sets the order of columns
        columns=dfmain.columns,
        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
        id='datatable-all'
    ), 
    dcc.Graph(
        id='graph-gapminder'
    ),
], className="container")

app.layout = serve_layout

# print(dfmain.to_dict('records'))


########################################################
#get and prepare new covid-19 data

@app.callback(
    # i'm imagining output as a hidden div, could be a dcc.Store or even user visible element
    Output("last-update", "children"),  
    [Input("refresh-data", "n_clicks")],  # if refresh-data is a button maybe you want n_clicks not value?
)
def refresh_data(value):
    print('data refresh is running')        
    completed = subprocess.run(['sudo', 'rm', '-r', 'COVID-19/'], \
                            stdout=subprocess.PIPE,)
    print(completed.stdout.decode('utf-8'))

    completed = subprocess.run(['git', 'clone', 'https://github.com/CSSEGISandData/COVID-19.git', 'COVID-19'], \
                            stdout=subprocess.PIPE,)
    print(completed.stdout.decode('utf-8'))

    mypath = 'COVID-19/csse_covid_19_data/csse_covid_19_daily_reports/'

    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f != 'README.md' and f != '.gitignore']
    onlyfiles.sort()
    print(onlyfiles[0], onlyfiles[-1])
    global firstdate
    global lastdate
    firstdate = onlyfiles[0][:-4]
    lastdate = onlyfiles[-1][:-4]

    i = 0
    for f in onlyfiles:
        # data format changed on 3-23
        if datetime.strptime(f[:-4] , '%m-%d-%Y') < datetime.strptime('03-22-2020', '%m-%d-%Y'):
            df = pd.read_csv(mypath + f)
            df = df[['Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered']]
            df = df.groupby(['Country/Region']).sum()
            df['Date'] = f[:-4]
            if i == 0:
                dfs = df
            if i > 0:
                dfs = pd.concat([dfs, df])
            i += 1
        else:
            df = pd.read_csv(mypath + f)
            df = df[['Province_State', 'Country_Region', 'Last_Update', 'Confirmed', 'Deaths', 'Recovered']]
            df.columns = ['Province/State', 'Country/Region', 'Last Update', 'Confirmed', 'Deaths', 'Recovered']
            df = df.groupby(['Country/Region']).sum()
            df['Date'] = f[:-4]
            if i == 0:
                dfs = df
            if i > 0:
                dfs = pd.concat([dfs, df])
            i += 1

    names = dfs.index.tolist()
    names = [x.strip() for x in names]
    changelist = [i for i, value in enumerate(names) if value == 'Mainland China']
    for c in changelist: names[c] = 'China'
    changelist = [i for i, value in enumerate(names) if value == 'Republic of Korea']
    for c in changelist: names[c] = 'South Korea'
    changelist = [i for i, value in enumerate(names) if value == 'Korea, South']
    for c in changelist: names[c] = 'South Korea'
    changelist = [i for i, value in enumerate(names) if value == 'Iran (Islamic Republic of)']
    for c in changelist: names[c] = 'Iran'
    changelist = [i for i, value in enumerate(names) if value == 'Iran (Islamic Republic of)']
    for c in changelist: names[c] = 'Iran'
    changelist = [i for i, value in enumerate(names) if value == 'occupied Palestinian territory']
    for c in changelist: names[c] = 'Israel'
    changelist = [i for i, value in enumerate(names) if value == 'United Kingdom']
    for c in changelist: names[c] = 'UK'
    changelist = [i for i, value in enumerate(names) if value == 'Hong Kong SAR']
    for c in changelist: names[c] = 'Hong Kong'
    changelist = [i for i, value in enumerate(names) if value == 'Taipei and environs']
    for c in changelist: names[c] = 'Taiwan'
    changelist = [i for i, value in enumerate(names) if value == 'Taiwan*']
    for c in changelist: names[c] = 'Taiwan'
    changelist = [i for i, value in enumerate(names) if value == 'Republic of Ireland']
    for c in changelist: names[c] = 'Ireland'
    changelist = [i for i, value in enumerate(names) if value == 'Czechia']
    for c in changelist: names[c] = 'Czech Republic'
    changelist = [i for i, value in enumerate(names) if value == 'Macau']
    for c in changelist: names[c] = 'Macao'
    changelist = [i for i, value in enumerate(names) if value == 'Macao SAR']
    for c in changelist: names[c] = 'Macao'
    changelist = [i for i, value in enumerate(names) if value == 'Republic of Moldova']
    for c in changelist: names[c] = 'Moldova'
    changelist = [i for i, value in enumerate(names) if value == 'Cote d\'Ivoire']
    for c in changelist: names[c] = 'Ivory Coast'
    changelist = [i for i, value in enumerate(names) if value == 'Viet Nam']
    for c in changelist: names[c] = 'Vietnam'
    changelist = [i for i, value in enumerate(names) if value == 'Russian Federation']
    for c in changelist: names[c] = 'Russia'
    changelist = [i for i, value in enumerate(names) if value == 'Congo (Kinshasa)']
    for c in changelist: names[c] = 'Congo'
    changelist = [i for i, value in enumerate(names) if value == 'DR Congo']
    for c in changelist: names[c] = 'Congo'
    changelist = [i for i, value in enumerate(names) if value == 'North Ireland']
    for c in changelist: names[c] = 'Ireland'
    changelist = [i for i, value in enumerate(names) if value == 'St. Martin']
    for c in changelist: names[c] = 'Saint Martin'
    dfs.index = names
    dfs.index.rename('Country', inplace=True)
    dfs['Date'] = pd.to_datetime(dfs['Date'])

    #get population data
    dfp = pd.read_csv('populations.csv')
    dfp.index = dfp.Country.values
    dfp.drop(['Country'], axis=1, inplace=True)
    dfp.index.rename('Country', inplace=True)

    #join with covid data
    dfsj = dfs.join(dfp, how='outer')
    dfsj['Population'] = pd.to_numeric(dfsj['Population'])
    dfsj.dropna(inplace=True)
    dfsj['Per1MConfCases'] = 1000000* dfsj.Confirmed/dfsj.Population
    dfsj['Per1MDeaths'] = 1000000* dfsj.Deaths/dfsj.Population

    #country as a col
    dfsj.reset_index(level=0, inplace=True)
    dfsj = dfsj.sort_values(['Country', 'Date'])

    #globals
    global dfd1
    global dfc1
    global dfmain
    global dfmain10

    #aligned by 1st death or case
    dfd1 = dfsj[dfsj['Deaths']>=20]
    dfc1 = dfsj[dfsj['Confirmed']>=600]

    #main table on latest date
    dfmain = dfsj.loc[dfsj.groupby(["Country"])["Date"].idxmax()]
    dfmain = dfmain.sort_values('Deaths', ascending=False)
    dfmain10 = dfmain.sort_values('Deaths', ascending=False).head(10)
    # dfmain10 = dfsj.loc[dfsj.groupby(["Country"])["Date"].idxmax()].head(10)
    # print(dfmain10)

    global lastupdated
    lastupdated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   
    return lastupdated




@app.callback(
    Output('datatable-gapminder', 'selected_row_indices'),
    [Input('graph-trends', 'clickData')],
    [State('datatable-gapminder', 'selected_row_indices')])
def update_selected_row_indices(clickData, selected_row_indices):
    if clickData:
        for point in clickData['points']:
            if point['pointNumber'] in selected_row_indices:
                selected_row_indices.remove(point['pointNumber'])
            else:
                selected_row_indices.append(point['pointNumber'])
    return selected_row_indices


@app.callback(
    Output('graph-gapminder', 'figure'),
    [Input('datatable-all', 'rows'),
     Input('datatable-all', 'selected_row_indices')])
def update_figure(rows, selected_row_indices):
    dff = pd.DataFrame(rows)
    fig = plotly.tools.make_subplots(
        rows=2, cols=1,
        # subplot_titles=('Deaths as % of Population', 'Cases as % of Population', '# of Deaths', '# of Cases'),
        subplot_titles=('# of Deaths', '# of Cases'),
        shared_xaxes=False)
    marker = {'color': ['#0074D9']*len(dff)}
    for i in (selected_row_indices or []):
        marker['color'][i] = '#FF851B'
    # fig.append_trace({
    #     'x': dff['Country'],
    #     'y': dff['PercPopDeaths'],
    #     'type': 'bar',
    #     'marker': marker
    # }, 1, 1)
    # fig.append_trace({
    #     'x': dff['Country'],
    #     'y': dff['PercPopConfirmed'],
    #     'type': 'bar',
    #     'marker': marker
    # }, 2, 1)
    fig.append_trace({
        'x': dff['Country'],
        'y': dff['Deaths'],
        'type': 'bar',
        'marker': marker
    }, 1, 1)
    fig.append_trace({
        'x': dff['Country'],
        'y': dff['Confirmed'],
        'type': 'bar',
        'marker': marker
    }, 2, 1)

    fig['layout']['showlegend'] = False
    fig['layout']['height'] = 1200
    fig['layout']['margin'] = {
        'l': 40,
        'r': 10,
        't': 60,
        'b': 200
    }
    fig['layout']['yaxis1']['type'] = 'linear'
    return fig





@app.callback(
    Output('graph-trends', 'figure'),
    [Input('datatable-gapminder', 'rows'),
     Input('datatable-gapminder', 'selected_row_indices')])
def update_figure(rows, selected_row_indices):
    dff = pd.DataFrame(rows)
    fig = plotly.tools.make_subplots(
        rows=4, cols=1,
        subplot_titles=( \
            '# of Deaths<br>(by Days Since 20th Death)', \
            '# of Deaths per 1M People<br>(by Days Since 20th Death)', \
                '# of Cases<br>(by Days Since 600th Case)', \
                '# of Confirmed Cases per 1M People<br>(by Days Since 600th Case)'), \
            # 'Deaths as % of Population<br>(by Calendar Date)', \
                # '# of Deaths as % of Population<br>(by Calendar Date)', \
                        # 'Cases as % of Population<br>(by Calendar Date)', \
                            # '# of Cases<br>(by Calendar Date)'),
        shared_xaxes=False)
    marker = {'color': ['#0074D9']*len(dff)}
    for i in (selected_row_indices or []):
        # print(i)
        # print(dff.Country[i])
        # print(dfsj['Date'][dfsj.Country.isin([dff.Country[i]])])
        # print(dfsj['PercPopDeaths'][dfsj.Country.isin([dff.Country[i]])])
        
        df0 = pd.DataFrame(data=[0], columns=['x'])
      
        fig.append_trace({
            # 'x': dfsj['Date'][dfsj.Country.isin([dff.Country[i]])],
            'y': pd.concat([df0['x'], dfd1['Deaths'][dfd1.Country.isin([dff.Country[i]])]]),
            'type': 'scatter',
            'mode': 'lines',
            'line': dict(color=plotlycolors[i]),
             "showlegend": False,
            'name':dff.Country[i]
        }, 1, 1)
        # print(pd.concat([df0['x'], dfd1['Deaths'][dfd1.Country.isin([dff.Country[i]])]]))
        fig.append_trace({
            # 'x': dfsj['Date'][dfsj.Country.isin([dff.Country[i]])],
            'y': pd.concat([df0['x'], dfd1['Per1MDeaths'][dfd1.Country.isin([dff.Country[i]])]]),
            'type': 'scatter',
            'mode': 'lines',
            'line': dict(color=plotlycolors[i]),
             "showlegend": False,
            'name':dff.Country[i]
        }, 2, 1)
        fig.append_trace({
            # 'x': dfsj['Date'][dfsj.Country.isin([dff.Country[i]])],
            'y': pd.concat([df0['x'], dfc1['Confirmed'][dfc1.Country.isin([dff.Country[i]])]]),
            'type': 'scatter',
            'mode': 'lines',
            'line': dict(color=plotlycolors[i]),
             "showlegend": True,
            'name':dff.Country[i]
        }, 3, 1)
        # print(pd.concat([df0['x'], dfc1['Confirmed'][dfc1.Country.isin([dff.Country[i]])]]))
        fig.append_trace({
            # 'x': dfsj['Date'][dfsj.Country.isin([dff.Country[i]])],
            'y': pd.concat([df0['x'], dfc1['Per1MConfCases'][dfc1.Country.isin([dff.Country[i]])]]),
            'type': 'scatter',
            'mode': 'lines',
            'line': dict(color=plotlycolors[i]),
             "showlegend": False,
            'name':dff.Country[i]
        }, 4, 1)
        
        # calendar date x axis
        # fig.append_trace({
        #     'x': dfsj['Date'][dfsj.Country.isin([dff.Country[i]])],
        #     'y': dfsj['PercPopDeaths'][dfsj.Country.isin([dff.Country[i]])],
        #     'type': 'scatter',
        #     'mode': 'lines',
        #     'line': dict(color=plotlycolors[i]),
        #      "showlegend": True,
        #     'name':dff.Country[i]
        # }, 1, 2)
        # fig.append_trace({
        #     'x': dfsj['Date'][dfsj.Country.isin([dff.Country[i]])],
        #     'y': dfsj['Deaths'][dfsj.Country.isin([dff.Country[i]])],
        #     'type': 'scatter',
        #     'mode': 'lines',
        #     'line': dict(color=plotlycolors[i]),
        #     'showlegend': False,
        #     'name':dff.Country[i]
        # }, 2, 2)
        # fig.append_trace({
        #     'x': dfsj['Date'][dfsj.Country.isin([dff.Country[i]])],
        #     'y': dfsj['PercPopConfirmed'][dfsj.Country.isin([dff.Country[i]])],
        #     'type': 'scatter',
        #     'mode': 'lines',
        #     'line': dict(color=plotlycolors[i]),
        #      "showlegend": False,
        #     'name':dff.Country[i]
        # }, 3, 2)
        # fig.append_trace({
        #     'x': dfsj['Date'][dfsj.Country.isin([dff.Country[i]])],
        #     'y': dfsj['Confirmed'][dfsj.Country.isin([dff.Country[i]])],
        #     'type': 'scatter',
        #     'mode': 'lines',
        #     'line': dict(color=plotlycolors[i]),
        #     'showlegend': False,
        #     'name':dff.Country[i]
        # }, 4, 2)


    # fig['layout']['title'] =' Cases and Deaths by Date')
    fig['layout']['height'] = 1200
    fig['layout']['margin'] = {
        'l': 40,
        'r': 10,
        't': 60,
        'b': 200
    }
    fig['layout']['yaxis1']['type'] = 'linear'
    return fig




# plotly_fig = mpl_to_plotly(mpl_fig)
# graph = dcc.Graph(id='myGraph', fig=plotly_fig)


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


if __name__ == '__main__':
    app.run_server(host='0.0.0.0',port=8888) # Domino hosts all apps at 0.0.0.0:8888
