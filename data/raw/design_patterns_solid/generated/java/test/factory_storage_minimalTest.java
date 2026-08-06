package org.example.patterns;
public class StorageFactoryTest {
    public static void main(String[] args) {
        StorageFactory f = new StorageFactory();
        if (!f.create("basic").operate().equals("basic-storage")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-storage")) throw new AssertionError();
        System.out.println("ok");
    }
}
