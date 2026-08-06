package org.example.patterns;
public class StorageStateTest {
    public static void main(String[] args) {
        StorageContext ctx = new StorageContext();
        if (!ctx.request().equals("was-off-storage")) throw new AssertionError();
        if (!ctx.request().equals("was-on-storage")) throw new AssertionError();
        System.out.println("ok");
    }
}
