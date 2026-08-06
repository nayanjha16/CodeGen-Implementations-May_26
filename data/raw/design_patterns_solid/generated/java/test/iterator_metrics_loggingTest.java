package org.example.patterns;
public class MetricsIteratorTest {
    public static void main(String[] args) {
        MetricsCollection col = new MetricsCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("metrics:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
