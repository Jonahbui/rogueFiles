/**
 * @Filename: n_root.java
 * @Author: Jonah Bui
 * @Version 1.00 2019/11/21
 * @Description: A program that calculates the nth root of a number for roots greater than 0.
 *  Attempts to apply this algorithm: https://en.wikipedia.org/wiki/Nth_root_algorithm
 */

public class n_root
{
    //Calculate the power of a number
    public static double myPOW(double value, int pow)
    {
		double result = 1;
		for(int i = 0; i < pow; i++)
		{
			result = result*value;
		}
		return result;
    }

    public static void main(String[] args)
    {
        //VARS
        int n = 5;          //Desired root (only works for integers > 0)
        double value = 5;   //Variable to take the n-th root of (only works for doubles > 0)

        //PROGRAM VALUES
		int precision = 64;	//Increase value to increase precision
		double result_error = 0;
		double guess = value/2;
		double lower = 0;
		double upper = value;
        //Implement algorithm for calculating the n-th root of a number
        for(int i = 0; i < precision; i++)
        {
			result_error = (1.0/(double)n)*(value/myPOW(guess, n-1)-guess);
			if(result_error < 0)
				upper = guess;
			else
				lower = guess;
			guess = (upper + lower)/2.0;
        }
        System.out.printf("The result error is: %.10f", result_error);
        System.out.printf("\nThe guess n-th root is: %.10f\n", guess);
    }
}
