/*
Author: Jonah Bui
Date: 5/06/19
Purpose: A program that plays the game Tic-Tac-Toe

How to play:
 - Enter the coordinates of the board which ranges from (0-2) in a pair with spaces.
	Ex. 1 0 would place a piece on row 1, column 0
*/

#include <stdio.h>
#include <string.h>

void playerMove(int player, int board[3][3]);
void printBoard(int board[3][3]);
void printPiece(int piece);
int winnerCheck(int board[3][3]);

int main(int argc, char **argv)
{
	//Make a board
	int board[3][3] =	{
					{0, 0, 0},
					{0, 0, 0},
					{0, 0, 0}
				};
	
	printBoard(board);

	//Loop until there is a winner
	int winner = 0;
	while(winner <= 0)
	{
		//Check if there is a winner before allowing the next player to take their turn
		if(winner == 0)
		{
			playerMove(1, board);
		}
		winner = winnerCheck(board);
		if(winner == 0)
		{
			playerMove(2, board);
		}
		winner = winnerCheck(board);
	}
	
	//Print out winner
	if(winner == 1 || winner == 2)
	{
		printf("The winner is player %d!\n",winner);
	}
	else if(winner == 3)
	{
		printf("It's a tie!\n");
	}
}	

void printBoard(int board[3][3])
{
	int i;
	printf("\n\n   | 0 | 1 | 2 |\n----------------\n");
	for(i = 0; i < 3; i++)
	{
		int j;
		printf("%2d |",i );
		for(j = 0; j < 3; j++)
		{
			printPiece(board[i][j]);
			printf("|");
		}
	printf("\n----------------\n");
	}

}

void printPiece(int piece)
{
	if(piece == 0)
	{
		printf("   ");
	}
	else if(piece == 1)
	{
		printf(" O ");
	}
	else if(piece == 2)
	{
		printf(" X ");
	}
}

void playerMove(int player, int board[3][3])
{
	printf("\nPlayer %d turn, enter coordinates: ", player);
	int xMove;
	int yMove;

	//Get input for x - row, y - column
	scanf("%d", &xMove);
	scanf("%d", &yMove);
	
	if(player == 1 && board[xMove][yMove] == 0)
	{
		board[xMove][yMove] = 1;
	}
	else if(player == 2 && board[xMove][yMove] == 0)
	{
		board[xMove][yMove] = 2;
	}
	else
	{
		printf("Invalid Move...");
	}
	printBoard(board);
}

int winnerCheck(int board[3][3])
{
	int winner = 0;
	int i;
	for(i = 0; i < 3; i++)
	{
		//Check for horizontal win
		if(board[i][0] == board[i][1] && board[i][1] == board [i][2] && board[i][0] > 0)
		{
			winner = board[i][0];
		}
		//Check for vertical win
		else if(board[0][i] == board[1][i] && board[1][i] == board[2][i] && board[0][i] > 0)
		{
			winner = board[0][i];
		}
	}
	
	//Check for diagonal wins
	if(board[0][0] == board[1][1] && board[1][1] == board[2][2] && board[0][0] > 0)
	{
		winner = board[0][0];
	}
	else if(board[2][0] == board[1][1] && board[1][1] == board[0][2] && board[2][0] > 0)
	{
		winner = board[2][0];
	}
	
	//Check if there is a tie
	int k;
	int tie = 1;
	for(k = 0; k < 3; k++)
	{
		int l;
		for(l = 0; l < 3; l++)
		{
			
			if(board[k][l] == 0)
			{
				tie = 0;		
			}	
		}
	}
	if(tie == 1 && winner <= 0)
	{
		winner = 3;
		return winner;
	}
	return winner;
}
