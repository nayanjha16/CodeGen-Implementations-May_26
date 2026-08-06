package org.example.patterns;
public class SyncDipTest {
    public static void main(String[] args) {
        String out = new SyncAppService(new SyncHttpGateway()).publish("p");
        if (!out.equals("http-sync:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}
