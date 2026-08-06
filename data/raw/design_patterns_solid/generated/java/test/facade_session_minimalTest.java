package org.example.patterns;
public class SessionFacadeTest {
    public static void main(String[] args) {
        SessionFacade f = new SessionFacade();
        if (!f.submit("x").equals("wrote-session:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
