/* 
    Genera, de forma recursiva los numeros de Fibonacci
*/
int fib(int n) {
    if (n <= 1) { return 1;}
    return fib(n-1) + fib(n-2);
}

int main(int argc, char *argv) {
    int n; 
    n = 20;

    printf(fib(n));

    return 0;
}
