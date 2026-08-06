package org.example.patterns;
public class NotificationsAbstractFactoryTest {
    public static void main(String[] args) {
        String out = NotificationsAbstractFactoryDemo.run(new NotificationsCloudFactory());
        if (!out.equals("cloud-btn-notifications|cloud-dlg-notifications")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
