package org.example.patterns;
public class MetricsPrototypeTest {
    public static void main(String[] args) {
        MetricsPrototype a = new MetricsPrototype("metrics", 2);
        MetricsPrototype b = a.copy();
        b.setLabel("metrics-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}
