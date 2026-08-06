package org.example.patterns;
public class StorageMementoTest {
    public static void main(String[] args) {
        StorageOriginator o = new StorageOriginator();
        StorageMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("storage-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
