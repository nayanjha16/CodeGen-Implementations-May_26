package org.example.patterns;
public class LoggingCompositeTest {
    public static void main(String[] args) {
        LoggingComposite root = new LoggingComposite();
        root.add(new LoggingLeaf(2));
        root.add(new LoggingLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
