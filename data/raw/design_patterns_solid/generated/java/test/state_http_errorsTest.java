package org.example.patterns;
public class HttpStateTest {
    public static void main(String[] args) {
        HttpContext ctx = new HttpContext();
        if (!ctx.request().equals("was-off-http")) throw new AssertionError();
        if (!ctx.request().equals("was-on-http")) throw new AssertionError();
        System.out.println("ok");
    }
}
