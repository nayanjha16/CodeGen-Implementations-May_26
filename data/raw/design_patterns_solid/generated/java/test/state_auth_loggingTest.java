package org.example.patterns;
public class AuthStateTest {
    public static void main(String[] args) {
        AuthContext ctx = new AuthContext();
        if (!ctx.request().equals("was-off-auth")) throw new AssertionError();
        if (!ctx.request().equals("was-on-auth")) throw new AssertionError();
        System.out.println("ok");
    }
}
