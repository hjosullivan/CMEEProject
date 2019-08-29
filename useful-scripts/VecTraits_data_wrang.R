## Script to subset the vectraits database for NLLS fitting ##

# Clear working environment
rm(list= ls())

# Set working directory because R likes to close for no reason
#setwd("~/Documents/CMEEProject/useful-scripts")

# Require necesary packages
require(tidyverse)

# Import data
df1 <- read.csv("../data/GlobalDataset_v0.71.csv", header = T, sep = ",", stringsAsFactors = F)

# Subset relavant columns
df1 <- df1 %>% 
  select(originalid,
         standardisedtraitvalue,
         standardisedtraitunit,
         standardisedtraitname,
         interactor1,
         interactor1kingdom,
         interactor1temp)

# Remove datasets without 2 unique temperatures above and below topt
df2 <- df1 %>% 
  group_by(originalid) %>%
  filter(any(cumsum(row_number() %in% c(which.max(standardisedtraitvalue) + - 2:2)) == 5))

# Remove datasets with 0 or negative values
df3 <- df2 %>% 
  filter(!is.na(standardisedtraitvalue), standardisedtraitvalue > 0)

# Remove datasets with less than 7 unique temperatures
df4 <- df3 %>% 
  group_by(originalid) %>% 
  dplyr::filter(length(unique(interactor1temp)) > 7)

# Add a column with temperature in Kelvins
df4[,"interactor1K"] <- df4[,"interactor1temp"] + 273.15

# Export clean data
write.csv(df4, file = "../data/curves.csv", row.names = F)

