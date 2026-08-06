package org.example.patterns;
public class SchedulingCompositeTest {
    public static void main(String[] args) {
        SchedulingComposite root = new SchedulingComposite();
        root.add(new SchedulingLeaf(2));
        root.add(new SchedulingLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
