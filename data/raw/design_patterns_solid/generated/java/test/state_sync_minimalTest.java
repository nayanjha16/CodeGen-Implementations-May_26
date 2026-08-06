package org.example.patterns;
public class SyncStateTest {
    public static void main(String[] args) {
        SyncContext ctx = new SyncContext();
        if (!ctx.request().equals("was-off-sync")) throw new AssertionError();
        if (!ctx.request().equals("was-on-sync")) throw new AssertionError();
        System.out.println("ok");
    }
}
