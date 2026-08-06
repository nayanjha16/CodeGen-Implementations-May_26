package org.example.patterns;
public class SyncFactoryTest {
    public static void main(String[] args) {
        SyncFactory f = new SyncFactory();
        if (!f.create("basic").operate().equals("basic-sync")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-sync")) throw new AssertionError();
        System.out.println("ok");
    }
}
