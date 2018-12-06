###################################
## Project timeline Gantt chart  ##
###################################

## Author: Hannah O'Sullivan h.osullivan18@imperial.ac.uk
## Script: gantt.R
## Desc: A gantt chart to describe my main project timeline
## Date: December 2018

# Clear environment
rm(list = ls())

# Require packages 
require(ggplot2)
require(reshape2)

# Create a dataframe of tasks
task1 <- c('Thesis writing', '2019-01-01', '2019-09-01')
task2 <- c('Data exploration', '2019-01-01', '2019-02-01')
task3 <- c('Literature review', '2019-01-01', '2019-02-01')
task4 <- c('Write python modules', '2019-02-01', '2019-03-01')
task5 <- c('Model fitting', '2019-03-01', '2019-04-01')
task6 <- c('Reevaluate models', '2019-03-01', '2019-05-01')
task7 <- c('Models comparison', '2019-05-01', '2019-07-01')
task8 <- c('Visualistion of results', '2019-06-01', '2019-07-01')
task9 <- c('Final push', '2019-07-01', '2019-09-30')

df <- as.data.frame(rbind(task1, task2, task3, task4, task5, task6, task7, task8, task9))
names(df) <- c('task', 'start', 'end')
df$task <- factor(df$task, levels = df$task)
df$start <- as.Date(df$start)
df$end <- as.Date(df$end)
df_melted <- melt(df, measure.vars = c('start', 'end'))

# Starting date to begin plot
start_date <- as.Date('2019-01-01')

# Plot using ggplot2
ggplot(df_melted, aes(value, task)) + 
  geom_line(size = 10) +
  labs(x = '', y = '',
       title = 'Project Timeline') +
  theme_bw(base_size = 20) +
  
  theme(plot.title = element_text(hjust = 0.5),
        panel.grid.major.x = element_line(colour="black", linetype = "dashed"),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        axis.text.x = element_text(angle = 0)) +
  scale_x_date(date_labels = "%b", limits = c(start_date, NA), date_breaks = '1 month')

# Save image to ../Data




