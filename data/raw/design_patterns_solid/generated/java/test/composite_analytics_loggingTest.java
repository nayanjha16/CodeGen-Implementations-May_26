package org.example.patterns;
public class AnalyticsCompositeTest {
    public static void main(String[] args) {
        AnalyticsComposite root = new AnalyticsComposite();
        root.add(new AnalyticsLeaf(2));
        root.add(new AnalyticsLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
