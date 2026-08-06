package org.example.patterns;
public class ProfileAbstractFactoryTest {
    public static void main(String[] args) {
        String out = ProfileAbstractFactoryDemo.run(new ProfileCloudFactory());
        if (!out.equals("cloud-btn-profile|cloud-dlg-profile")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
