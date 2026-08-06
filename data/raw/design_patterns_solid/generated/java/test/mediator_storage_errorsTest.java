package org.example.patterns;
public class StorageMediatorTest {
    public static void main(String[] args) {
        StorageMediator m = new StorageMediator();
        new StorageColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}
