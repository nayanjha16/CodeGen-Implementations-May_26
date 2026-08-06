package org.example.patterns;
public class StorageChainTest {
    public static void main(String[] args) {
        StorageHandler h = new StorageLowHandler();
        h.link(new StorageHighHandler());
        if (!h.handle(2, "m").equals("high-storage:m")) throw new AssertionError();
        System.out.println("ok");
    }
}
