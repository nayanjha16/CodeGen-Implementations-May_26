package org.example.patterns;
public class NotificationsCompositeTest {
    public static void main(String[] args) {
        NotificationsComposite root = new NotificationsComposite();
        root.add(new NotificationsLeaf(2));
        root.add(new NotificationsLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}
