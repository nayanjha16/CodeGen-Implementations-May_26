package org.example.patterns;
public class HttpMementoTest {
    public static void main(String[] args) {
        HttpOriginator o = new HttpOriginator();
        HttpMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("http-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
