package org.example.patterns;
public class NotificationsIspTest {
    public static void main(String[] args) {
        NotificationsStore st = new NotificationsStore();
        st.write("x");
        if (!NotificationsIspClient.mirror(st).equals("notifications:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
