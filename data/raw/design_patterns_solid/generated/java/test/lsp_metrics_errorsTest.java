package org.example.patterns;
public class MetricsLspTest {
    public static void main(String[] args) {
        MetricsShape[] arr = new MetricsShape[] { new MetricsRectangle(2,3), new MetricsSquare(4) };
        if (MetricsLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
