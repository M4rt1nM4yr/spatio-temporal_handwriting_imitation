
def findSmallestMultipleOf(num, multiplier):
    numInt = int(num)
    multiplierInt = int(multiplier)

    numberOfTimes = (numInt-1)//multiplierInt
    return (numberOfTimes+1)*multiplierInt
