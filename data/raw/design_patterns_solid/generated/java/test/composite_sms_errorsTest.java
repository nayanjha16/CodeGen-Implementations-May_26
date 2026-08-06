package org.example.patterns;
public class SmsCompositeTest {
    public static void main(String[] args) {
        SmsComposite root = new SmsComposite();
        root.add(new SmsLeaf(2));
        root.add(new SmsLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
