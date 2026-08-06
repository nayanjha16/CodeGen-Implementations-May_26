package org.example.patterns;
public class StorageFacadeTest {
    public static void main(String[] args) {
        StorageFacade f = new StorageFacade();
        if (!f.submit("x").equals("wrote-storage:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
