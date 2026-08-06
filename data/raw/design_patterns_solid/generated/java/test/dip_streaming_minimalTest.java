package org.example.patterns;
public class StreamingDipTest {
    public static void main(String[] args) {
        String out = new StreamingAppService(new StreamingHttpGateway()).publish("p");
        if (!out.equals("http-streaming:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
