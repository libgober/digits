#source is Hill, A Statistical Derivation of the Significant Digit Law
#confirmed with table from https://www.agacgfm.org/AGA/FraudToolkit/documents/BenfordsLaw.pdf
benford1 <- function(d){log10(1+1/d)}
benford2 <- function(d){
  sto = 0
  for (k in 1:9){
    sto= sto + benford1(10*k+d)}
  return(sto)
}
benford3 <- function(d){
  sto = 0
  for (d1 in 1:9){
    for (d2 in 0:9){
      sto = sto + benford1(100*d1 + 10*d2+d)
    }
  }
  return(sto)
}

p1 = c(0,benford1(1:9))
p2 = benford2(0:9)
p3 = benford3(0:9)
1 - c(sum(p1),sum(p2),sum(p3)) < 10^-10
#weights = c(1/3,1/3,1/3)
weights = c(1/3,1/3,1/3)
###### BEGIN SIM
nsims=50
waittime = NULL
minstart = 100
for (sim in 1:nsims){
  rejected = FALSE
  draws = NULL
  law.selected = NULL
  while (rejected == FALSE){
    law.selected = c(law.selected,sample(1:3,1,prob=weights))
    p = eval(parse(text=eval(paste0("p",law.selected[-1]))))
    new.d = sample(x=0:9,size=1,replace=T,prob=p)
    draws = c(draws,new.d)
    if (length(draws) >= minstart){
      counts =table(factor(draws,levels=1:9))
      test = chisq.test(counts,correct=FALSE)
      rejected = test$p.value < 0.05
    }
  }
  waittime = c(waittime,length(draws))
}
hist(waittime,main="How Many Precincts to Lookat Before \n Rejecting Uniform at 95% Only First 2 Laws")
  