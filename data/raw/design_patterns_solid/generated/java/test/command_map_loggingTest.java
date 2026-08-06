package org.example.patterns;
public class MapCommandTest {
    public static void main(String[] args) {
        MapCommand cmd = new MapActionCommand(new MapReceiver(), "x");
        if (!cmd.execute().equals("done-map:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
