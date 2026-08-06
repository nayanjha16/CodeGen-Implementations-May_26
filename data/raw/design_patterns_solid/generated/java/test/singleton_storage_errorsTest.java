package org.example.patterns;
public class StorageSingletonTest {
    public static void main(String[] args) {
        StorageSingleton a = StorageSingleton.getInstance();
        StorageSingleton b = StorageSingleton.getInstance();
        a.setValue("storage-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("storage-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}
