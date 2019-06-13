library(copula)

args <- commandArgs(TRUE)
## parameters for the first beta marginal
alpha1 <- as.double(args[1])
beta1 <- as.double(args[2])

## parameters for the 2nd beta marginal
alpha2 <- as.double(args[3])
beta2 <- as.double(args[4])

## correlation coefficient
corr <- as.double(args[5])

## sample size
N <- as.double(args[6])


cop2 <- mvdc(normalCopula(c(corr), dim=2, dispstr="un"), 
	  		c("beta", "beta"),list(list(shape1=alpha1, shape2=beta1), 
	  		list(shape1 = alpha2, shape2=beta2)))

Q <- rMvdc(N, cop2)
q <- as.data.frame(Q)

#output_file <- as.character(args[7])
#write.csv(q, file = output_file)
print(q)


