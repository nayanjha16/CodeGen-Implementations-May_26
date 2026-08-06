package org.example.patterns;
public class SmsFacadeTest {
    public static void main(String[] args) {
        SmsFacade f = new SmsFacade();
        if (!f.submit("x").equals("wrote-sms:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
