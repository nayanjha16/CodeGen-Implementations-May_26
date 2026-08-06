package org.example.patterns;
public class SessionDipTest {
    public static void main(String[] args) {
        String out = new SessionAppService(new SessionHttpGateway()).publish("p");
        if (!out.equals("http-session:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
