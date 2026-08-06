package org.example.patterns;
public class SessionAbstractFactoryTest {
    public static void main(String[] args) {
        String out = SessionAbstractFactoryDemo.run(new SessionCloudFactory());
        if (!out.equals("cloud-btn-session|cloud-dlg-session")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
