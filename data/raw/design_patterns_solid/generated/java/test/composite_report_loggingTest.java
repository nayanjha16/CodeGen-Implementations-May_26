package org.example.patterns;
public class ReportCompositeTest {
    public static void main(String[] args) {
        ReportComposite root = new ReportComposite();
        root.add(new ReportLeaf(2));
        root.add(new ReportLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
