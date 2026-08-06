package org.example.patterns;
public class HttpCommandTest {
    public static void main(String[] args) {
        HttpCommand cmd = new HttpActionCommand(new HttpReceiver(), "x");
        if (!cmd.execute().equals("done-http:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
