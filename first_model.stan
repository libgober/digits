data {
  int<lower=0> J; // number of precincts 
  int<lower=0> candidate_votes[J,4]; //4 column matrix of votes for each party
}
parameters {
  real AKP[J]; //untransformed proportion of AKP votes
  real MHP[J]; //untransformed proportion of MHP votes
  real CHP[J]; //untransformed proportion of CHP votes
  real OTHER[J]; //untransformed proportion of OTHER votes
  real mu_AKP; //hyperparameter of mean of AKP proportions
  real sigma_AKP; //hyperparameter of sd of AKP proportions
  real mu_MHP; //
  real sigma_MHP; //
  real mu_CHP; //
  real sigma_CHP; //
  real mu_OTHER; //
  real sigma_OTHER; //
}
transformed parameters {
  vector[4] temp[J]; //for storing the pre-transformed proportions
  simplex[4] proportions[J]; //for storing the post-transformation proportions
  for (j in 1:J) {
  temp[j,1] <- AKP[j];
  temp[j,2] <- MHP[j];
  temp[j,3] <- CHP[j];
  temp[j,4] <- OTHER[j];
  }
  for (j in 1:J) proportions[j] <- softmax(temp[j]); //transform proportions
}
model {
  for (j in 1:J) AKP[j] ~ normal(mu_AKP,exp(sigma_AKP)); 
  for (j in 1:J) MHP[j] ~ normal(mu_MHP,exp(sigma_MHP));
  for (j in 1:J) CHP[j] ~ normal(mu_CHP,exp(sigma_CHP));
  for (j in 1:J) OTHER[j] ~ normal(mu_OTHER,exp(sigma_OTHER));
  for (j in 1:J) candidate_votes[j] ~ multinomial(proportions[j]);
}