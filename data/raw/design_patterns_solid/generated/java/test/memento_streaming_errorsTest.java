package org.example.patterns;
public class StreamingMementoTest {
    public static void main(String[] args) {
        StreamingOriginator o = new StreamingOriginator();
        StreamingMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("streaming-init")) throw new AssertionError();
        System.out.println("ok");
    }
}
