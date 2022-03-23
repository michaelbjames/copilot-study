use std::{time::Instant};


fn main() {
    let now = Instant::now();
    let result = fib(50);
    println!("Result: {}", result);
    println!("Time: {}ms", now.elapsed().as_millis());
    plot_fib();
}

// Efficient Fibonacci
fn fib(n: u64) -> u64 {
    if n < 2 {
        return n;
    }
    let mut a = 0;
    let mut b = 1;
    for _ in 0..n {
        let c = a + b;
        a = b;
        b = c;
    }
    return b;
}

// Plot the Fibonacci sequence
fn plot_fib() {
    use plotters::prelude::*;
    let root = BitMapBackend::new("fib.png", (200, 200)).into_drawing_area();
    root.fill(&WHITE).unwrap();
    let N_MAX = 50;
    let max_val = (fib(N_MAX) as f64).log10();
    let mut chart = ChartBuilder::on(&root)
        .caption("Fibonacci Sequence", ("sans-serif", 24).into_font())
        .build_cartesian_2d(0u64..N_MAX, 0u64..(max_val as u64)).unwrap();
    chart.configure_mesh().draw().unwrap();


    chart.draw_series(LineSeries::new(
        (0..N_MAX).map(|x| (x, (fib(x) as f64).log10() as u64)),
        &RED,
    )).unwrap();

}