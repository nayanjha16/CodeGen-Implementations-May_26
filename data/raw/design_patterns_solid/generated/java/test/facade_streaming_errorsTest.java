package org.example.patterns;
public class StreamingFacadeTest {
    public static void main(String[] args) {
        StreamingFacade f = new StreamingFacade();
        if (!f.submit("x").equals("wrote-streaming:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
