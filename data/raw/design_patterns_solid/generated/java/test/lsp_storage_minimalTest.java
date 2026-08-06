package org.example.patterns;
public class StorageLspTest {
    public static void main(String[] args) {
        StorageShape[] arr = new StorageShape[] { new StorageRectangle(2,3), new StorageSquare(4) };
        if (StorageLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}
