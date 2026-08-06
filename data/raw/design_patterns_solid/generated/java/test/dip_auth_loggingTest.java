package org.example.patterns;
public class AuthDipTest {
    public static void main(String[] args) {
        String out = new AuthAppService(new AuthHttpGateway()).publish("p");
        if (!out.equals("http-auth:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
