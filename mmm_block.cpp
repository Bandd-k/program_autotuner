#include <stdio.h>
#include <cstdlib>

#define N 500

int main(int argc, const char** argv)
{

  int n = BLOCK_SIZE * (N/BLOCK_SIZE);
  double a[N][N];
  double b[N][N];
  double c[N][N];
  double sum = 0;
  for(int k1=0;k1<n;k1+=BLOCK_SIZE)
  {
      for(int j1=0;j1<n;j1+=BLOCK_SIZE)
      {
          for(int k1=0;k1<n;k1+=BLOCK_SIZE)
          {
              for(int i=0;i<n;i++)
              {
                  for(int j=j1;j<j1+BLOCK_SIZE;j++)
                  {
                      sum = c[i][j];
                      for(int k=k1;k<k1+BLOCK_SIZE;k++)
                      {
                          sum += a[i][k] * b[k][j];
                      }
                      c[i][j] = sum;
                  }
              }
          }
      }
  }
  printf("%f", c[0][0]);
  return 0;
}