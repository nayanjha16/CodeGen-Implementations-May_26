package org.example.patterns;
public class ProfileStateTest {
    public static void main(String[] args) {
        ProfileContext ctx = new ProfileContext();
        if (!ctx.request().equals("was-off-profile")) throw new AssertionError();
        if (!ctx.request().equals("was-on-profile")) throw new AssertionError();
        System.out.println("ok");
    }
}
