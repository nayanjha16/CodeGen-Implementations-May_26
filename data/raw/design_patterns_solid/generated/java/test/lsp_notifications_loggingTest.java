package org.example.patterns;
public class NotificationsLspTest {
    public static void main(String[] args) {
        NotificationsShape[] arr = new NotificationsShape[] { new NotificationsRectangle(2,3), new NotificationsSquare(4) };
        if (NotificationsLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
