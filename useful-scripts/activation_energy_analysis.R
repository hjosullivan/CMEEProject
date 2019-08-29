# Clear environment
rm(list = ls())

# Load required packages
library(tidyverse)
library(ggthemes)

# Define functions

# Bootstrap the mean to get confidence intervals (95%)
boot_mean <- function(x){
  reps <- numeric(10000)
  for(i in 1:10000) reps[i] <- mean(sample(x, replace = T))
  quantile(reps, c(.025, .975))
}

# Bootstrap the median to get confidence intervals (95%)
boot_median <- function(x){
  reps <- numeric(10000)
  for(i in 1:10000) reps[i] <- median(sample(x, replace = T))
  quantile(reps, c(.025, .975))
}

# Import data set
df <- read.csv("final_data.csv")

# Only keep activation energy values between 0 and 3
df_sub <- df %>% 
  dplyr::filter(estimate > 0, estimate < 3, !is.na(standardisedtraitname))

### 1. Comparison of activation energy by traits, intra- and interspecific
##########################################################################
# Define intra- and interspecific groups
df_sub$group[df_sub$standardisedtraitname %in% c("Growth", "Photosynthesis", "Respiration")] <- "Intraspecific hierarchy"
df_sub$group[df_sub$standardisedtraitname %in% c("Consumption", "Encounter", "Foraging Velocity")] <- "Interspecific hierarchy"
df_sub$group <- as.factor(df_sub$group)

# Calculate median and bootstrap confidence intervals by trait
df_trait_comp <- df_sub %>%
  dplyr::group_by(standardisedtraitname, group) %>% 
  dplyr::summarise(trait_median = median(estimate),
            trait_median_low = boot_median(estimate)[1],
            trait_median_high = boot_median(estimate)[2],
            trait_mean = mean(estimate),
            trait_mean_low = boot_mean(estimate)[1],
            trait_mean_high = boot_mean(estimate)[2]) 

# Define factor level order for plot
df_trait_comp$standardisedtraitname <- factor(df_trait_comp$standardisedtraitname, 
                                                 levels = c("Growth", "Photosynthesis", "Respiration", "Encounter", "Foraging Velocity", "Consumption"))

### FIGURE 1 of results
jpeg(file="fig1_traits_median.jpg", width = 300, height = 150, units = "mm", res = 300)
ggplot2::ggplot(df_trait_comp) + 
  geom_errorbar(aes(x=standardisedtraitname, ymin=trait_mean_low, ymax=trait_mean_high, col = standardisedtraitname),
                lwd = 1.2, width=.05, alpha=1) +
  geom_point(aes(standardisedtraitname, trait_mean, col = standardisedtraitname), pch=16, cex=3) +
  ggthemes::theme_few() +
  facet_wrap(facets = "group", ncol = 2, scales = "free") +
  xlab("") +
  ylab("Median activation energy (eV)") +
  theme(legend.position = "none",
        axis.text=element_text(size=10)) +
  geom_hline(yintercept = 0.65, linetype = "dashed", alpha = .3) +
  scale_color_manual(values = c("#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2"))
dev.off()

### 2. Comparison of activation energy by traits, within kingdoms
#################################################################
# Calculate median and bootstrap confidence intervals by trait and kingdom
df_trait_kingdom <- df_sub %>%
  dplyr::group_by(standardisedtraitname, interactor1kingdom) %>% 
  dplyr::summarise(trait_median = median(estimate),
                   trait_median_low = boot_median(estimate)[1],
                   trait_median_high = boot_median(estimate)[2],
                   trait_mean = mean(estimate),
                   trait_mean_low = boot_mean(estimate)[1],
                   trait_mean_high = boot_mean(estimate)[2]) 

# Select set of traits per kingdom
df_trait_kingdom_sub <- df_trait_kingdom %>% 
  filter(interactor1kingdom == "Metazoa" & standardisedtraitname == "Encounter" | 
           interactor1kingdom == "Metazoa" & standardisedtraitname == "Foraging Velocity" | 
           interactor1kingdom == "Metazoa" & standardisedtraitname == "Consumption" | 
           interactor1kingdom == "Bacteria" & standardisedtraitname == "Photosynthesis" | 
           interactor1kingdom == "Bacteria" & standardisedtraitname == "Growth" |
           interactor1kingdom == "Plantae" & standardisedtraitname == "Photosynthesis" | 
           interactor1kingdom == "Plantae" & standardisedtraitname == "Respiration" | 
           interactor1kingdom == "Fungi" & standardisedtraitname == "Growth" | 
           interactor1kingdom == "Fungi" & standardisedtraitname == "Respiration")

# Add line breaks for the plot
levels(df_trait_kingdom_sub$standardisedtraitname) <- gsub(" ", "\n", levels(df_trait_kingdom_sub$standardisedtraitname))

### FIGURE 2 of results
jpeg(file="fig2_kingdom_trait_median.jpg", width = 300, height = 200, units = "mm", res = 300)
ggplot2::ggplot(df_trait_kingdom_sub) + 
  geom_errorbar(aes(x=standardisedtraitname, ymin=trait_median_low, ymax=trait_median_high, col = standardisedtraitname),
                lwd = 1.2, width=.05, alpha=1) +
  geom_point(aes(standardisedtraitname, trait_median, col = standardisedtraitname), pch=16, cex=3) +
  facet_wrap(~interactor1kingdom, scales = "free") +
  ggthemes::theme_few() +
  xlab("") +
  ylab("Median activation energy (eV)") +
  theme(legend.position = "none") +
  scale_color_manual(values = c("#0072B2", "#009E73", "#F0E442", "#000000", "#E69F00", "#56B4E9"))
dev.off()


### 3. Comparison of activation energy exemplified by one kingdom and one trait, compared between climates
##########################################################################################################
# Calculate median and bootstrap confidence intervals by trait, kingdom and climate
df_climate <- df_sub %>%
  dplyr::group_by(climate, interactor1kingdom, standardisedtraitname) %>% 
  dplyr::summarise(trait_median_low = boot_median(estimate)[1],
            trait_median_high = boot_median(estimate)[2],
            trait_median = median(estimate),
            trait_mean = mean(estimate),
            trait_mean_low = boot_mean(estimate)[1],
            trait_mean_high = boot_mean(estimate)[2]) %>% 
  dplyr::filter(!is.na(climate))

# Subset data to Bacteria and Growth only
df_sub_climate <- df_climate %>% 
  dplyr::filter(interactor1kingdom == "Bacteria" & standardisedtraitname == "Growth")

# Reorder factor levels of climate for plot
df_sub_climate$climate <- factor(df_sub_climate$climate, levels = c("cold zone", "temperate", "sub-tropical", "tropical"))

### FIGURE 3 of results
jpeg(file="fig3_kingdom_climate_mean.jpg", width = 150, height = 150, units = "mm", res = 300)
ggplot(df_sub_climate, aes(x=standardisedtraitname)) + 
  geom_errorbar(aes(ymin=trait_median_low, ymax=trait_median_high, col = climate), 
                width=.2, alpha=.5, lwd = 1.3, position=position_dodge(width=0.5)) +
  geom_point(aes(y=trait_median, col = climate),
             pch = 16, cex = 3, position=position_dodge(width=0.5), alpha = 1) +
  ggtitle("Bacteria") +
  ggthemes::theme_few() +
  xlab("") +
  ylab("Median activation energy (eV)") +
  scale_color_manual(values = c("#3371FF", "#169F38", "#FFA833", "#EE3927")) 
dev.off()


