use std::env;
fn main() {
}

fn fib(n: u32) -> u32 {
    if n == 0 {
        return 0;
    }
    if n == 1 {
        return 1;
    }
    // fyb is misspelled!
    // Does your rust setup point this out?
    return fyb(n - 1) + fib(n - 2);
}