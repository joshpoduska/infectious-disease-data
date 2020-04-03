***YOU MUST FORK THIS PROJECT TO MAKE IT YOUR OWN. THIS ENABLES STARTING WORKSPACES, RUNNING JOBS, CREATING SCHEDULED JOBS, AND PUBLISHING APPs AND MODEL APIs***

***To encourage more analytical insight of the COVID-19 pandemic, Domino is offering extended use of the Medium and Large compute 
tiers for qualified organizations while removing the usual time restrictions on this trial site. Please reach out to Domino by 
clicking on the blue chat button to the lower right corner of this screen. Once your request is verified, you will be added to 
the COVID19-research organization and given these enhanced privileges at no charge over the life of the trial.***

# Welcome to the Infectious Disease Data Project

### The goal of this project is to provide a central repository for popular disease and health data to empower analysts and researchers.

### Browse the Files for details.

### Three scheduled jobs are setup on this project. As you are not the project owner, you cannot see them but you may want to consider creating them yourself. They are simple and run code/covid19-JHU.ipynb, code/cdcfluview.R, and  code/data_exploration_n_viz.ipynb each once a day. The first two load fresh data into the data directory under Files. The last simply creates new visualizations in the notebook.

### Data Descriptions:

- [2019 Novel Coronavirus Data Repository by Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19) - Confirmed cases and 
deaths by country. Updated daily.
- [Population data](https://www.worldometers.info/world-population/population-by-country/) - Manually created csv file. Static.
- [CDC Flu View](https://cran.r-project.org/web/packages/cdcfluview/index.html) - Downloads of the most popular CDC data 
sources via the R package, cdcfluview. Updated daily.
- [Italy Flu Baseline](https://www.sciencedirect.com/science/article/pii/S1201971219303285#tbl0015) - Very rough estimates
of Itallian flu deaths over a four year period based on academic research models. Only max and min values for each flu
season are estimated. Consider adding a baseline of 0.78 deaths per 100,000 people to each value in this dataset as the 
Italian model put flu deaths at zero in weeks in and around summer. 0.78 per 100,000 is the US minimum per CDC flu and pnemonia
tracking.

***Search the [Domino Support Site](https://docs.dominodatalab.com/en/4.0/) for answers to commonly asked questions.***
