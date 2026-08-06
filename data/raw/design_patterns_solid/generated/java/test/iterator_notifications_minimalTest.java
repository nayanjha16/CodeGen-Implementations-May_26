package org.example.patterns;
public class NotificationsIteratorTest {
    public static void main(String[] args) {
        NotificationsCollection col = new NotificationsCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("notifications:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
