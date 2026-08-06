package org.example.patterns;
public class CacheMementoTest {
    public static void main(String[] args) {
        CacheOriginator o = new CacheOriginator();
        CacheMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("cache-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
