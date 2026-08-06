package org.example.patterns;
public class AuthAbstractFactoryTest {
    public static void main(String[] args) {
        String out = AuthAbstractFactoryDemo.run(new AuthCloudFactory());
        if (!out.equals("cloud-btn-auth|cloud-dlg-auth")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
