##Takes a CDF passed as a string as its first argument
##Takes a raw digits string as its second argument

## To debug the following commands may be useful, since they can replace the commandArgs input
# n = 100
# cdfstring = paste(rep(.1*n,10),collapse="---")
# raw_digits_string = paste(sample(n),collapse ="---")

  suppressMessages(require(dgof))
  cdfstring = commandArgs(trailingOnly=TRUE)[1]
  null_expected = as.numeric(strsplit(cdfstring,"---")[[1]])
  if (sum(null_expected) != 0){
  freq = function(x){
    x/sum(x)
  }
  cumulate <- function(x){
    sto = 0
    for (i in 1:length(x)){
      sto = c(sto,sum(x[1:i]))
    }
    sto
  }
  p<-cumulate(freq(null_expected))
  sim_ecdf<-stepfun(0:9,p)
  raw_digits_string = commandArgs(trailingOnly=TRUE)[2]
  raw_digits = as.numeric(strsplit(raw_digits_string,"---")[[1]])
  real_raw_digits  = raw_digits %% 10
  test = ks.test(real_raw_digits,y=sim_ecdf,simulate.p.value = TRUE,B=100)
  cat(test$p.value)
  }
  