package org.example.patterns;
public class AnalyticsIteratorTest {
    public static void main(String[] args) {
        AnalyticsCollection col = new AnalyticsCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("analytics:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
