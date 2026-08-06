package org.example.patterns;
public class AuthSrpTest {
    public static void main(String[] args) {
        AuthRecord r = new AuthRecord("a", 3);
        if (!new AuthFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}
